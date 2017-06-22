from api.models import *
from api.game import perform_resolve
import shlex
import readline
import atexit
from tabulate import tabulate
from argparse import ArgumentParser, Namespace


class ParserError(BaseException):
    pass


class RepeatingArgumentParser(ArgumentParser):
    def error(self, message):
        raise ParserError(message)


def setup_parser():
    parser = RepeatingArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(dest='command')

    help_cmd = subparsers.add_parser('help', help='Shows help')

    setup_cmd = subparsers.add_parser('setup', help='Sets up environment')
    setup_cmd.add_argument('client_id', nargs='?', default=None, help='Sets the client ID')

    register_cmd = subparsers.add_parser('register', help='Registers client')
    register_cmd.add_argument('display_name', help='Client\'s name')
    register_cmd.add_argument('phone', help='Client\'s phone number')
    register_cmd.add_argument('--bot', action='store_true', default=False, help='Makes the user a bot')
    register_cmd.add_argument('--energy', default='1:5', help='Energy parameters')

    profile_cmd = subparsers.add_parser('profile', help='Show currently loaded profile')
    profile_cmd.add_argument('--client-id', default=None, help='ID of the profile to show')

    games_cmd = subparsers.add_parser('games', help='List of games')

    game_cmd = subparsers.add_parser('game', help='Show game detail')
    game_cmd.add_argument('game_id')
    game_cmd.add_argument('--delete', action='store_true', default=False, help='Delete the game after showing info')

    start_cmd = subparsers.add_parser('start', help='Start a game')
    start_cmd.add_argument('versus')
    start_cmd.add_argument('rounds', type=int)

    play_cmd = subparsers.add_parser('play', help='Play in a game')
    play_cmd.add_argument('game_id', type=int)
    play_cmd.add_argument('move')

    return parser


class Context:
    def __init__(self):
        self.parser = None
        self.client_id = None
        self.client = None

    def help_handler(self, args):
        self.parser.print_help()

    def setup_handler(self, args):
        if not args.client_id:
            self.client_id = str(uuid.uuid4())
        else:
            self.client_id = args.client_id

        print("Client ID:", self.client_id)

        qs = Client.objects.filter(id=self.client_id)
        if qs.exists():
            self.client = qs.first()
            print("Loaded client:", self.client.profile.display_name)

    def register_handler(self, args):
        client = Client(id=self.client_id)

        profile = Contact.objects.create(contact_id=0, contact_key='profile',
                                         display_name=args.display_name)
        profile_raw = profile.raw_contacts.create(contact_type='com.android.profile', contact_name='Profile')
        profile_raw.data.create(type='NAME', value=args.display_name)
        profile_raw.data.create(type='PHONE', value=args.phone)
        client.profile = profile

        if args.bot:
            client.is_bot = True

        pool_size, regen_rate = args.energy.split(':')
        client.energy = Energy(pool_size=pool_size, regen_rate=regen_rate)
        client.energy.save()

        client.save()

        print("Registered client:", client.profile.display_name)
        self.client = client

    def profile_handler(self, args):
        if args.client_id:
            client = Client.objects.get(id=args.client_id)
        else:
            client = self.client

        print("=== Profile", client.id, "===")
        for data in client.profile.data:
            print(data.type, ":", data.value)

    def games_handler(self, args):
        def format_rounds(game, rounds):
            my_player = game.player_set.filter(client=self.client).first()
            icons = []
            for rnd in rounds:
                if rnd.number == game.current_round:
                    if rnd.move_set.filter(player=my_player).exists():
                        icons.append("✓")
                    elif rnd.move_set.count() > 0:
                        icons.append("!")
                    else:
                        icons.append("?")
                elif rnd.winner is None:
                    icons.append("🤷")
                elif rnd.winner == my_player:
                    icons.append("👍")
                else:
                    icons.append("👎")

            icons += ["\u2205"] * (game.rounds_num - len(icons))

            return str.join(" ", icons)

        print("=== Games ===")
        print(tabulate([(game.id, game.status, "{}/{}".format(game.current_round, game.rounds_num), format_rounds(game, game.rounds_ordered)) for game in self.client.games], headers=['ID', 'Status', 'Progress', 'Rounds']))

    def game_handler(self, args):
        def format_moves(moves):
            return str.join(" ", ["({} {})".format(move.player_id, move.move) for move in moves]) or "\u2205"

        game = Game.objects.get(id=args.game_id)

        print("=== Game", game.id, "===")
        print("Status:", dict(Game.STATUS)[game.status])
        print("Num Rounds:", game.rounds_num)

        print("Players:")
        for player in game.player_set.order_by('id').all():
            print(" - {}: {}".format(player.id, player.client.profile.display_name))

        print("Rounds:")
        for rnd in game.rounds_ordered:
            print(" - {}: {}".format(rnd.id, format_moves(rnd.move_set.order_by('player_id'))))

        if args.delete:
            game.delete()
            print("Game deleted")

    def start_handler(self, args):
        try:
            the_game = Game.objects.create(rounds_num=args.rounds)
            the_game.player_set.create(client=self.client)
            the_game.player_set.create(client=Client.objects.get(id=args.versus))

            the_game.rounds.create(number=1)

            the_game.save()
            print("Started game", the_game.id)
        except:
            print("Failed to create the game!")

    def play_handler(self, args):
        game = Game.objects.get(id=args.game_id)
        if not game.over:
            player = game.player_set.get(client=self.client)
            rnd = game.rounds.get(number=game.current_round)
            rnd.move_set.create(player=player, move=args.move)

            print("Made Move")

            round_complete, game_complete = perform_resolve(game, rnd)
            print("Round: {}, Game: {}".format(round_complete, game_complete))


HANDLERS = {
    'help': Context.help_handler,
    'setup': Context.setup_handler,
    'register': Context.register_handler,
    'profile': Context.profile_handler,
    'games': Context.games_handler,
    'game': Context.game_handler,
    'start': Context.start_handler,
    'play': Context.play_handler,
}


def run(*varargs):
    histfile = ".client_shell_history"
    try:
        readline.read_history_file(histfile)
        # default history len is -1 (infinite), which may grow unruly
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

    atexit.register(readline.write_history_file, histfile)

    context = Context()
    context.parser = setup_parser()
    running = True

    if len(varargs) > 0:
        client_id = varargs[0]
        context.setup_handler(Namespace(client_id=client_id))

    while running:
        try:
            cmd = input("> ")
            readline.add_history(cmd)
            argv = shlex.split(cmd)
            args = context.parser.parse_args(argv)

            if args.command in HANDLERS:
                handler = HANDLERS[args.command]
                handler(context, args)
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            exit(0)
        except EOFError:
            print("Done")
            exit(0)
        except ParserError as ex:
            print("Error:", ex.args[0])
            context.parser.print_usage()
        except Exception as ex:
            print("Exception ({}): {}".format(type(ex), ex.args))

