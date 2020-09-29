import json
import os

import discord
import requests
from discord.ext import commands

octobot_prefix = '^'
description = """
Hi There! I'm a bot written to provide some GitHub utilities on Discord.
"""
zwsp = "​"
gh_api_header = {"Accept": "application/vnd.github.v3+json"}
octobot = commands.Bot(command_prefix=octobot_prefix, description=description)


@octobot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(octobot))


@octobot.event
async def on_message(message):
    if message.author == octobot.user:
        return
    await octobot.process_commands(message)


@octobot.command()
async def user(ctx, username):
    url = "https://api.github.com/users/{0}".format(username)
    res = requests.get(url, headers=gh_api_header)
    if res.status_code == 200:
        data = res.json()
        res_embed = discord.Embed(
            title=data['name'] if data['name'] else data['login'],
            url=data['html_url']
        )

        res_embed.add_field(name=("Username" if data["type"] == "User" else
                                  "Organisation Name"), value=data['login'],
                            inline=False)

        if data['bio']:
            res_embed.add_field(name="Bio", value=data['bio'], inline=False)
        res_embed.set_thumbnail(url=data['avatar_url'])

        res_embed.add_field(name="Repos", value="[{0}]({1})".format(
            data['public_repos'],
            data['html_url'] + "?tab=repositories"
        ))

        res_embed.add_field(name="Gists", value="[{0}]({1})".format(
            data['public_gists'],
            "https://gist.github.com/" + data['login']
        ))

        if data["type"] == "user":
            res_embed.add_field(name="Followers", value="[{0}]({1})".format(
                                data['followers'],
                                data['html_url'] + "?tab=followers"
                                ))

            res_embed.add_field(name="Following", value="[{0}]({1})".format(
                                data['following'],
                                data['html_url'] + "?tab=following"
                                ))

            if data['company']:
                res_embed.add_field(name="Company", value=data['company'])

        if data['location']:
            res_embed.add_field(name="Location", value=data["location"])

        orgs = ["[{0}]({1})".format(x['login'], "https://github.com/" +
                                    x['login']) for x in requests.get(
            data['organizations_url'], headers=gh_api_header).json()]

        if orgs:
            res_embed.add_field(
                name="Organisation" + ("s" if len(orgs) > 1 else ""),
                value=" and ".join(orgs) if len(orgs) <= 2 else (", ".join(
                    orgs[:2]) + ", and {0} others".format(len(orgs) - 2))
            )

        if data['email']:
            res_embed.add_field(
                name="Email", value="[{0}]({0})".format(data['email']))

        if data['blog']:
            res_embed.add_field(name="Website", value="[{0}]({0})".format(
                (data["blog"] if (data["blog"].startswith(
                    "http://") or data["blog"].startswith("https://")) else
                    ("http://" + data["blog"]))))

        if data['twitter_username']:
            res_embed.add_field(
                name="Twitter", value="[{0}](https://twitter.com/{0})".format(
                    data["twitter_username"]))

    elif res.status_code == 404:
        res_embed = discord.Embed(
            title="User not found",
            description="User `{0}` was not found.".format(username),
            color=0xFF0000
        )

    await ctx.send(embed=res_embed)


USER = os.getenv('OCTOBOT_DISCORD_KEY')
octobot.run(USER)
