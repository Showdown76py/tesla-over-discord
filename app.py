import json
import requests
import teslapy
import os
import discord
import logging
import dotenv
from discord import app_commands, Interaction
import base64


dotenv.load_dotenv()
allowed_user_ids = [int(a) for a in os.environ["ALLOWED_USERIDS"].split(",")]
logger = logging.getLogger("tesla-notifications-discord")

class Formatting(logging.Formatter):

    light_blue = '\033[1;36m'
    blue = "\033[1;34m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "\033[1;30m{asctime} [c]{levelname:<8} \033[0;35m{name} \033[0m{message}"

    FORMATS = {
        logger.DEBUG: format.replace('[c]',light_blue),
        logging.INFO: format.replace('[c]',blue),
        logging.WARNING: format.replace('[c]',yellow),
        logging.ERROR: format.replace('[c]',red),
        logging.CRITICAL: format.replace('[c]',bold_red)
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S', style='{')
        return formatter.format(record)

# formatter = logging.Formatter('', datefmt=,style='{')
handler = logging.StreamHandler()
handler.setFormatter(Formatting())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

selected_car = None
tesla = None
vehicles = []
intents = discord.Intents.default()
intents.members = True

class App(discord.Client):
    def __init__(self, *, intents: discord.Intents) -> None:
        logger.info("Initializing App")
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self) -> None:
            await self.tree.sync()

app = App(intents=intents)

@app.event
async def on_interaction(interaction: Interaction) -> None:
    if interaction.user.id in allowed_user_ids:
        pass
    else:
        await interaction.response.send_message("You are not an authorized user!")

def get_vehicle_data():
    global selected_car
    vehicle: teslapy.Vehicle = vehicles[selected_car]
    vehicle.sync_wake_up()
    vehicle_data = vehicle.get_vehicle_data()
    logger.DEBUG(vehicle_data)
    return json.loads(str(vehicle_data))

@app.event
async def on_ready() -> None:
    global selected_car, tesla, vehicles
    logger.info("Discord bot is ready")

    # Initializing TeslaPy
    logger.info("Initializing TeslaPy")
    tesla = teslapy.Tesla(email=os.environ["TESLA_EMAIL"])
    if not tesla.authorized:
        print('Your are currently not logged in to Tesla')
        print('Please follow this link, then paste the URL after you are logged in.')
        print(tesla.authorization_url())
        print('\nURL after login: ', end='')
        url = input()

        tesla.fetch_token(authorization_response=url)
        print('You are now logged in to Tesla')
    
    vehicles = tesla.vehicle_list()
    logger.info('Successfully logged in\nRecognized vehicles:')
    for vehicle in vehicles:
        print(f'  - {vehicle["display_name"]}')
    
    logger.info("TeslaPy is ready")
    logger.debug('Bot is now fully ready.')
    logger.warning('will only work with the first car found in the list. This will change in the future and will support multiple cars.')
    selected_car = 0

sentrymode = app_commands.tree.Group(
    name="sentrymode",
    description="Sentry Mode related commands"
)

def authorized_users_only(interaction: Interaction, **kwargs) -> bool:
    return interaction.user.id in allowed_user_ids

@sentrymode.command(
    name="activate",
    description="Activate Sentry Mode"
)
@app_commands.check(authorized_users_only)
async def activate(interaction: Interaction) -> None:
    global selected_car
    logger.debug("activate command called")
    await interaction.response.defer()
    vehicle: teslapy.Vehicle = vehicles[selected_car]
    vehicle.sync_wake_up()
    vehicle.command('SET_SENTRY_MODE', on=True)
    await interaction.followup.send("👀 Sentry Mode **activated**")



@sentrymode.command(
    name="deactivate",
    description="Deactivate Sentry Mode"
)
@app_commands.check(authorized_users_only)
async def deactivate(interaction: Interaction) -> None:
    global selected_car
    logger.debug("deactivate command called")
    await interaction.response.defer()
    vehicle: teslapy.Vehicle = vehicles[selected_car]
    vehicle.sync_wake_up()
    vehicle.command('SET_SENTRY_MODE', on=False)
    await interaction.followup.send("👀 Sentry Mode **deactivated**")

app.tree.add_command(sentrymode)

commands = app_commands.tree.Group(
    name="commands",
    description="Basic commands for controlling your Tesla"
)

@commands.command(
    name='flash-lights',
    description="Flash the headlights"
)
@app_commands.check(authorized_users_only)
async def flash_headlights(interaction: Interaction) -> None:
    global selected_car
    logger.debug("flash-headlights command called")
    await interaction.response.defer()
    vehicle: teslapy.Vehicle = vehicles[selected_car]
    vehicle.sync_wake_up()
    vehicle.command('FLASH_LIGHTS')
    await interaction.followup.send("🚦 Flashed headlights")

@commands.command(
    name='honk-horn',
    description="Honk the horn"
)
@app_commands.check(authorized_users_only)
async def honk_horn(interaction: Interaction) -> None:
    global selected_car
    logger.debug("honk-horn command called")
    await interaction.response.defer()
    vehicle: teslapy.Vehicle = vehicles[selected_car]
    vehicle.sync_wake_up()
    vehicle.command('HONK_HORN')
    await interaction.followup.send("📢 **Honking** horn")

@commands.command(
    name="ventilate",
    description="Ventilate the car (opens the windows slightly)"
)
@app_commands.check(authorized_users_only)
async def ventilate(interaction: Interaction) -> None:
    global selected_car
    logger.debug("ventilate command called")
    await interaction.response.defer()
    vehicle: teslapy.Vehicle = vehicles[selected_car]
    vehicle.sync_wake_up()
    # Check if the windows are already opened
    close = False
    if get_vehicle_data()['vehicle_state']['fd_window'] != 0:
        close = True
    vehicle.command('WINDOW_CONTROL', command='vent' if not close else "close", lat=0, lon=0)
    await interaction.followup.send("🪟 **Ventilating** (opening windows)" if not close else "🪟 **Closing windows**")


app.tree.add_command(commands)

climate = app_commands.tree.Group(
    name="climate",
    description="Climate related commands"
)

@climate.command(
    name="heat",
    description="Start the climate"
)
@app_commands.check(authorized_users_only)
async def start_climate(interaction: Interaction) -> None:
    global selected_car
    logger.debug("start command called")
    await interaction.response.defer()
    vehicle: teslapy.Vehicle = vehicles[selected_car]
    vehicle.sync_wake_up()
    vehicle.command('CLIMATE_ON')
    await interaction.followup.send("🌡️ **Starting climate**")

@app.tree.command(
    name="trunk",
    description="Open/Close the trunk or the frunk."
)
@app_commands.choices(which=[
    app_commands.Choice(name="Rear", value="Rear"),
    app_commands.Choice(name="Front", value="Front"),
])
@app_commands.check(authorized_users_only)
async def open_chests(interaction: Interaction, which: app_commands.Choice[str]) -> None:
    global selected_car
    logger.debug("open_chests command called")
    await interaction.response.defer()
    vehicle: teslapy.Vehicle = vehicles[selected_car]
    vehicle.sync_wake_up()
    if which.value == "Rear":
        vehicle.command('ACTUATE_TRUNK', which_trunk="rear")
    elif which.value == "Front":
        vehicle.command('ACTUATE_TRUNK', which_trunk='front')
    await interaction.followup.send(f"🚪 Actuating **{which.value} trunk**")

@climate.command(
    name="stop",
    description="Stop the climate"
)
@app_commands.check(authorized_users_only)
async def stop_climate(interaction: Interaction) -> None:
    global selected_car
    logger.debug("stop command called")
    await interaction.response.defer()
    vehicle: teslapy.Vehicle = vehicles[selected_car]
    vehicle.sync_wake_up()
    vehicle.command('CLIMATE_OFF')
    await interaction.followup.send("🌡️ **Stopping climate**")

app.tree.add_command(climate)

@app.tree.command(
    name="info",
    description="Get informations about your car"
)
@app_commands.check(authorized_users_only)
async def info(interaction: Interaction) -> None:
    global selected_car
    logger.debug("info command called")
    await interaction.response.defer()
    vehicle: teslapy.Vehicle = vehicles[selected_car]
    vehicle.sync_wake_up()
    data = get_vehicle_data()
    embed = discord.Embed()
    embed.color = discord.Color.red()
    embed.set_author(name='Your Tesla Model ' + vehicle['vin'][3])
    logger.DEBUG(data)
    embed.title = f"{data['display_name']}"
    # Vehicle Image
    # TODO: Option Codes deprecated
    if data['option_codes'] is None or data['option_codes'] == []:
        if 'CUSTOM_OPTIONS' in os.environ.keys():
            opt_codes = os.environ['CUSTOM_OPTIONS'].split(',')
    else: opt_codes = data['option_codes']
    logger.DEBUG(opt_codes)
    img = vehicle.compose_image(size=1024, options=','.join(opt_codes))
    img_url=requests.post(
        'https://freeimage.host/api/1/upload',
        data={
            'key': '6d207e02198a847aa98d0a2a901485a5', # This is a public key, safe to put in the source code. Change it if you want.
            'action': 'upload',
            'format': 'json',
            'source': base64.b64encode(img).decode('utf-8'),
        }
    ).json()['image']['url']
    embed.set_image(url=img_url)

    embed.description = 'Your car is **'+('locked' if data['vehicle_state']['locked'] else 'unlocked')+'**'
    embed.description += '\nSentry Mode is **'+('enabled' if data['vehicle_state']['sentry_mode'] else 'disabled')+'**'
    if data['climate_state']['is_climate_on']:
        embed.description += '\nClimate is **on** (going to **' + str(data['climate_state']['driver_temp_settings']) + '°C**)'
    if data['vehicle_state']['software_update']['status'] != '':
        embed.description += '\n**An update is available!**'

    # Vehicle Data
    # Get loaction
    l = requests.get(f'https://nominatim.openstreetmap.org/reverse.php?lat={data["drive_state"]["latitude"]}&lon={data["drive_state"]["longitude"]}&format=jsonv2').json()
    embed.add_field(name='Location', value=f"{l['address']['municipality']}\n||**{l['address']['road']}** || *(click to reveal)*")
    embed.add_field(name='Inside Temperature', value=f"{int(data['climate_state']['inside_temp'])}°C")
    embed.add_field(name='Outside Temperature', value=f"{int(data['climate_state']['outside_temp'])}°C")
    embed.add_field(name=('Not Charging' if data['charge_state']['charging_state'] == 'Disconnected' else "Charging"), value=f"**Battery Level:** {int(data['charge_state']['battery_level'])}% ({int(data['charge_state']['battery_range']*1.609)} km)")

    formatted_odometer = format(int(data['vehicle_state']['odometer']*1.609)+1, ',d').replace(',', ' ')
    status = 'Parked'
    if data['drive_state']['shift_state'] is not None:
        if data['drive_state']['shift_state'] == 'D':
            status = 'Driving'
        elif data['drive_state']['shift_state'] == 'R':
            status = 'Reversing'
        elif data['drive_state']['shift_state'] == 'P':
            status = 'Parked'
        elif data['drive_state']['shift_state'] == 'N':
            status = 'Neutral'
        else:
            status = 'Unknown'
    
    if status != 'Parked':
        embed.description += f"\n**Driving Speed:** {int(data['drive_state']['speed']*1.609)} km/h"

    embed.set_footer(text='Software '+data['vehicle_state']['car_version'].split(' ')[0] + ' — ' + str(formatted_odometer) + ' km — '+status)

    # TODO: finish
    await interaction.followup.send(embed=embed)

@app.tree.command(
    name="unlock",
    description='Unlocks your Tesla'
)
@app_commands.check(authorized_users_only)
async def unlock(interaction: Interaction) -> None:
    global selected_car
    logger.debug("unlock command called")
    await interaction.response.defer()
    vehicle: teslapy.Vehicle = vehicles[selected_car]
    vehicle.sync_wake_up()
    vehicle.command('UNLOCK')
    await interaction.followup.send('🔓 **'+vehicle['display_name']+'** is now unlocked')

@app.tree.command(
    name="lock",
    description='Locks your Tesla'
)
@app_commands.check(authorized_users_only)
async def unlock(interaction: Interaction) -> None:
    global selected_car
    logger.debug("lock command called")
    await interaction.response.defer()
    vehicle: teslapy.Vehicle = vehicles[selected_car]
    vehicle.sync_wake_up()
    vehicle.command('LOCK')
    await interaction.followup.send('🔓 **'+vehicle['display_name']+'** is now unlocked')



app.run(os.environ["DISCORD_TOKEN"])

        
