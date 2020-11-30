import discord
from discord import Intents
import logging
import regex as re


class RegexClient(discord.Client):
    def __init__(self):
        member_intent = Intents(guilds=True, members=True, emojis=True, messages=True)
        super().__init__(intents=member_intent)

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == client.user:
            return

        print(f'Raw Message from {message.author}: {message.content}')
        cleaned_message = clean_message_text(message)
        print(f'\tCleaned Message: {cleaned_message}')

        pingables = get_pingables(message)
        print(f'\tPingables: {pingables}')

        potential_pings = get_potential_pings(cleaned_message)
        print(f'\tPotential Pings: {potential_pings}')

        matching_pingables = get_matching_pingables(pingables, potential_pings)
        if len(matching_pingables) > 0:
            output_message_text = ' '.join(pingable.mention for pingable in matching_pingables)
            print(f'\tSending pings: {output_message_text}')

            await message.channel.send(output_message_text)
        else:
            print('\t No valid pings found')


def get_matching_pingables(pingables, potential_pings):
    matching_pingables = []
    for pingable in pingables:
        pingable_name = get_name(pingable)
        pingable_pattern = get_regex(pingable_name)
        for ping in potential_pings:
            if re.match(pingable_pattern, ping):
                matching_pingables.append(pingable)
                break
    return matching_pingables


CHANNEL_MENTION_PATTERN = re.compile('<#(\\d+)>')
EMOJI_PATTERN = re.compile('<:[^:]+?:(\\d+)>')
USER_MENTION_PATTERN = re.compile('<@!(\\d+)>')
ROLE_MENTION_PATTERN = re.compile('<@&(\\d+)>')


def clean_message_text(message):
    # channel mentions
    cleaned_message = re.sub(CHANNEL_MENTION_PATTERN,
                             lambda match: f'#{get_name(client.get_channel(int(match.group(1))))}',
                             message.content)

    # emojis
    cleaned_message = re.sub(EMOJI_PATTERN,
                             lambda match: f':{get_name(client.get_emoji(int(match.group(1))))}:',
                             cleaned_message)

    guild = message.channel.guild
    if guild is not None:
        # user mentions with nickname
        cleaned_message = re.sub(USER_MENTION_PATTERN,
                                 lambda match: f'@{get_name(guild.get_member(int(match.group(1))))}',
                                 cleaned_message)

        # role mentions
        cleaned_message = re.sub(ROLE_MENTION_PATTERN,
                                 lambda match: f'@{get_name(guild.get_role(int(match.group(1))))}',
                                 cleaned_message)
    else:
        # user mentions in non-guild channels
        cleaned_message = re.sub(USER_MENTION_PATTERN,
                                 lambda match: f'@{get_name(client.get_user(int(match.group(1))))}',
                                 cleaned_message)
    return cleaned_message


POTENTIAL_PING_PATTERN = re.compile('@(.*)')


def get_potential_pings(message_text):
    matches = re.findall(POTENTIAL_PING_PATTERN, message_text, overlapped=True)
    return matches


def get_pingables(message):
    channel = message.channel
    guild = channel.guild
    pingable_members = list(filter(lambda member: is_regex(get_name(member)), channel.members))
    pingable_roles = list(filter(lambda role: role.mentionable and is_regex(get_name(role)), guild.roles))
    pingables = pingable_members + pingable_roles
    return pingables


def is_regex(name):
    if not (len(name) >= 2 and name[0] == name[-1] == '/'):
        return False

    try:
        get_regex(name)
    except re.error:
        return False

    return True


def get_regex(name):
    return re.compile(name[1:-1], re.IGNORECASE)


def get_name(pingable):
    if isinstance(pingable, discord.Member):
        return pingable.display_name
    elif pingable is not None:
        return pingable.name
    else:
        return ''


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    client = RegexClient()
    with open('token.txt') as key_file:
        key = key_file.readline()
    client.run(key)
