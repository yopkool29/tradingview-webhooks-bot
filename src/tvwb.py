import json
import os
from subprocess import run

from utils.copy_template import copy_from_template
from utils.formatting import snake_case
from utils.log import get_logger
from utils.modify_settings import add_action, delete_action, add_event, link_action_to_event, unlink_action_to_event
from utils.validators import CustomName

import typer

# GUI management functions
def clear_gui_key():
    try:
        os.remove('.gui_key')
    except FileNotFoundError:
        pass

def generate_gui_key():
    import secrets
    if not os.path.exists('.gui_key'):
        open('.gui_key', 'w').write(secrets.token_urlsafe(24))

def read_gui_key():
    return open('.gui_key', 'r').read()

def print_gui_info(open_gui: bool, host: str, port: int):
    if open_gui:
        print('GUI is set to [OPEN] - it will be served at the root path.')
        print(f'\n\tView GUI dashboard here: http://{host}:{port}\n')
    else:
        key = read_gui_key()
        print('GUI is set to [CLOSED] - it will be served at the path /?guiKey=<unique_key>')
        print(f'\n\tView GUI dashboard here: http://{host}:{port}?guiKey={key}\n')
        print('To run the GUI in [OPEN] mode (for development purposes only), run: tvwb start --open-gui')
        gui_modes_url = 'https://github.com/robswc/tradingview-webhooks-bot/discussions/43'
        print(f'To learn more about GUI modes, visit: {gui_modes_url}')

def run_server(host: str, port: int, workers: int):
    print("Close server with Ctrl+C in terminal.")
    run(f'waitress-serve --listen={host}:{port} --threads={workers} wsgi:app'.split(' '))

app = typer.Typer()
logger = get_logger(__name__)

# configure logging


@app.command('start')
def start(
        open_gui: bool = typer.Option(
            default=False,
            help='Determines whether the GUI should be served at the root path, or behind a unique key.',
        ),
        host: str = typer.Option(
            default='localhost'
        ),
        port: int = typer.Option(
            default=5000
        ),
        workers: int = typer.Option(
            default=1,
            help='Number of workers to run the server with.',
        )
):
    if open_gui:
        clear_gui_key()
    else:
        generate_gui_key()

    print_gui_info(open_gui, host, port)
    run_server(host, port, workers)


@app.command('action:create')
def create_action(
        name: str,
        register: bool = typer.Option(
            ...,
            prompt='Register action?',
            help="Automatically register this event upon creation.",
        ),
):
    """
    Creates a new action.
    """
    logger.info(f'Creating new action --->\t{name}')

    custom_name = CustomName(name)
    copy_from_template(
        source='components/actions/base/template/action_template.py',
        target=f'components/actions/{custom_name.snake_case()}.py',
        tokens=['_TemplateAction_', 'TemplateActionClass', 'template_action'],
        replacements=[custom_name.snake_case(), custom_name.camel_case(), custom_name.snake_case()])

    logger.info(f'Action "{name}" created successfully!')

    if register:
        add_action_to_settings(name)

    return True


@app.command('action:register')
def add_action_to_settings(
        name: str
):
    """
    Registers an action to the actions registry. (Adds to settings.py)
    """
    logger.info(f'Registering action --->\t{name}')
    add_action(name)
    return True


@app.command('action:link')
def action_link(
        action_name: str,
        event_name: str
):
    """
    Links an action to an event.
    """
    logger.info(f'Setting {event_name} to trigger --->\t{action_name}')
    link_action_to_event(action_name, event_name)


@app.command('action:unlink')
def action_unlink(
        action_name: str,
        event_name: str
):
    """
    Unlinks an action from an event.
    """
    logger.info(f'Unlinking {action_name} from {event_name}')
    unlink_action_to_event(action_name, event_name)


@app.command('action:remove')
def remove_action_from_settings(
        name: str,
        force: bool = typer.Option(
            ...,
            prompt="Are you sure you want to remove this action from settings.py?",
            help="Force deletion without confirmation.",
        ),
):
    """
    Removes action from settings.py (unregisters it)
    If you wish to delete the action file, that must be done manually.
    """
    logger.info(f'Deleting action --->\t{name}')
    if force:
        delete_action(name)
    else:
        typer.echo("Aborted!")
    return True


@app.command('event:create')
def create_event(name: str):
    logger.info(f'Creating new event --->\t{name}')

    custom_name = CustomName(name)

    copy_from_template(
        source='components/events/base/template/event_template.py',
        target=f'components/events/{custom_name.snake_case()}.py',
        tokens=['_TemplateEvent_', 'TemplateEventClass', 'template_event'],
        replacements=[f'{custom_name.snake_case()}', custom_name.camel_case(), custom_name.snake_case()])

    logger.info(f'Event "{name}" created successfully!')
    return True


@app.command('event:register')
def register_event(name: str):
    """
    Registers an event to the events registry. (Adds to settings.py)
    """
    logger.info(f'Registering event --->\t{name}')
    try:
        add_event(name)
    except Exception as e:
        logger.error(e)


@app.command('event:trigger')
def trigger_event(name: str):
    logger.info(f'Triggering event --->\t{name}')
    event = getattr(__import__(f'components.events.{snake_case(name)}', fromlist=['']), name)()
    event.trigger({})
    return True


@app.command('util:send-webhook')
def send_webhook(key: str):
    logger.info(f'Sending webhook')
    post_data = json.dumps({
        "test": "data",
        "key": key})
    run(['curl', '-X', 'POST', '-H', 'Content-Type: application/json', '-d', post_data,
         'http://localhost:5000/webhook'])


if __name__ == "__main__":
    app()
