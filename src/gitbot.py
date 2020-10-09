import datetime
import asyncio
import json
import math
import os

import discord
import requests
from discord.ext import commands

import help

gitbot_prefix = 'gh!'
description = """
Hi There! I'm a bot written to provide some GitHub utilities on Discord.
"""
zwsp = "​"
gh_api_header = {"Accept": "application/vnd.github.v3+json"}

GH_USER = os.getenv('GITBOT_GITHUB_USER')
GH_ACCESS_TOKEN = os.getenv('GITBOT_GITHUB_TOKEN')
gitbot_auth = requests.auth.HTTPBasicAuth(GH_USER, GH_ACCESS_TOKEN)

gitbot = commands.Bot(
    command_prefix=gitbot_prefix,
    description=description,
    help_command=help.CustomHelpCommand()
)


# Helper funcs

async def format_time(in_str_time):
    return datetime.datetime.strptime(
        in_str_time, "%Y-%m-%dT%H:%M:%SZ"
    ).strftime("%mᵗʰ %b '%y %H:%M")


# Discord funcs

@gitbot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(gitbot))


@gitbot.event
async def on_message(message):
    if message.author == gitbot.user:
        return
    await gitbot.process_commands(message)


@gitbot.command()
async def repo(ctx, owner_user, repo_name):
    """
    Returns information about `repo_name` owned by `owner_user`
    """

    url = "https://api.github.com/repos/{0}/{1}".format(owner_user, repo_name)
    res = requests.get(url, headers=gh_api_header, auth=gitbot_auth)
    if res.status_code == 200:
        data = res.json()
        res_embed = discord.Embed(
            title=data['name'],
            url=data['html_url']
        )

        if data['description']:
            res_embed.add_field(name="Description",
                                value=data['description'], inline=False)
        res_embed.set_thumbnail(url=data['owner']['avatar_url'])

        res_embed.add_field(name="Language", value="{0}".format(
            data['language']
        ))

        res_embed.add_field(name="License", value=("[{0}]({1})".format(
            data['license']['name'],
            data['html_url'] + '/blob/' + data['default_branch'] + '/LICENSE')
            if data['license'] else "None")
        )

        res_embed.add_field(name="Open Issues",
                            value="[{0}]({1})".format(
                                data["open_issues_count"],
                                data['html_url'] + "/issues")
                            )

        res_embed.add_field(name="Stars",
                            value="[{0}]({1})".format(
                                data["stargazers_count"],
                                data['html_url'] + "/stargazers")
                            )

        res_embed.add_field(name="Watchers",
                            value="[{0}]({1})".format(
                                data["watchers_count"],
                                data['html_url'] + "/watchers")
                            )

        res_embed.add_field(name="Forks",
                            value="[{0}]({1})".format(
                                data["forks"],
                                data['html_url'] + "/network/members")
                            )

        res_embed.add_field(name="Default Branch",
                            value="[{0}]({1})".format(
                                data["default_branch"],
                                data['html_url'] + "/tree/" +
                                data['default_branch'])
                            )

        contri_res = requests.get(
            data['contributors_url'], headers=gh_api_header, auth=gitbot_auth)

        if contri_res.status_code == 200:
            contributors = ["[{0}]({1})".format(x['login'], "https://github.com/" +
                                                x['login']) for x in contri_res.json()]

            if contributors:
                res_embed.add_field(
                    name="Contributor" +
                    ("s" if len(contributors) > 1 else ""),
                    value=" and ".join(contributors) if len(contributors) <= 2 else
                    (", ".join(contributors[:2]) + ", and {0} others".format(
                        len(contributors) - 2)
                     )
                )
        elif contri_res.status_code == 403:
            res_embed.add_field(
                name="Contributors",
                value="Too many to show"
            )

        if data['fork']:
            res_embed.add_field(
                name="Fork",
                value="This repo is a fork of {0}".format(
                    data['parent']['full_name']
                ),
                inline=False
            )

            res_embed.add_field(
                name="Parent",
                value="[{0}]({1})".format(
                    data['parent']['full_name'],
                    data['parent']['html_url']
                )
            )

            res_embed.add_field(
                name="Source",
                value="[{0}]({1})".format(
                    data['source']['full_name'],
                    data['source']['html_url']
                )
            )

        res_embed.add_field(name="Clone URL", value="`{0}`".format(
            data["clone_url"]), inline=False)

        res_embed.add_field(name="SSH URL", value="`{0}`".format(
            data["ssh_url"]), inline=False)

        res_embed.set_footer(
            text="Created: {0} \nLast Commit: {1} \nLast Push: {2}".format(
                await format_time(data['created_at']),
                await format_time(data['updated_at']),
                await format_time(data['pushed_at'])
            )
        )

    elif res.status_code == 404:
        res_embed = discord.Embed(
            title="Repo not found",
            description="Repo `{0}` owned by `{1}` was not found.".format(
                repo_name, owner_user),
            color=0xFF0000
        )

    await ctx.send(embed=res_embed)


@gitbot.command()
async def followers(ctx, username):
    """
    Returns followers of GitHub user `username`
    """
    async def get_page(n):
        params = {
            "page": n,
            "per_page": 20
        }
        res = requests.get(
            url,
            params=params,
            headers=gh_api_header,
            auth=gitbot_auth
        )

        if res.status_code == 200:
            data = res.json()
            res_embed = discord.Embed(
                title="Followers of {0}".format(name),
                url=user_data['html_url']
            )

            res_embed.set_footer(text="Page {0} of {1}".format(n, total_pages))

            for i in data:
                res_embed.add_field(
                    name=i['login'],
                    value=i['html_url'],
                    inline=False
                )

            success = True

        elif res.status_code == 404:
            res_embed = discord.Embed(
                title="User not found",
                description="User `{0}` was not found.".format(username),
                color=0xFF0000
            )
            success = False
        return res_embed, success

    parent_res = requests.get(
        "https://api.github.com/users/{0}".format(username),
        headers=gh_api_header,
        auth=gitbot_auth
    )
    user_data = parent_res.json()
    total_followers = user_data['followers']
    name = user_data['name'] if user_data['name'] else user_data['login']
    total_pages = math.ceil(total_followers / 20)
    url = "https://api.github.com/users/{0}/followers".format(username)
    res_embed, exit_code = await get_page(1)
    msg = await ctx.send(embed=res_embed)
    if not exit_code:
        return
    await msg.add_reaction("⬅️")
    await msg.add_reaction("◀️")
    await msg.add_reaction("▶️")
    await msg.add_reaction("➡️")
    current_page = 1

    while current_page in range(1, total_pages + 1):
        try:
            reaction, _user = await gitbot.wait_for(
                'reaction_add',
                timeout=60,
                check=lambda reaction, user: str(reaction.emoji) in [
                    "◀️", "▶️", "⬅️", "➡️"] and user.id == ctx.author.id
            )
        except asyncio.TimeoutError:
            timeup_embed = msg.embeds[0]
            timeup_embed.set_footer(text="No longer accepting input")
            timeup_embed.color = 0xFF0000
            await msg.edit(embed=timeup_embed)
            break
        else:
            if str(reaction.emoji) == "◀️":
                current_page -= 1
            elif str(reaction.emoji) == "▶️":
                current_page += 1
            elif str(reaction.emoji) == "⬅️":
                current_page = 1
            elif str(reaction.emoji) == "➡️":
                current_page = total_pages
            current_page = min(max(1, current_page), total_pages)
            new_embed, exit_code = await get_page(current_page)
            await msg.edit(embed=new_embed)


@gitbot.command()
async def user(ctx, username):
    """
    Returns information about GitHub user `username`
    """

    url = "https://api.github.com/users/{0}".format(username)
    res = requests.get(url, headers=gh_api_header, auth=gitbot_auth)
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
                                        data['organizations_url'],
                                        headers=gh_api_header,
                                        auth=gitbot_auth
        ).json()]

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

        res_embed.set_footer(
            text="Created: {0} \nLast Commit: {1}".format(
                await format_time(data['created_at']),
                await format_time(data['updated_at'])
            )
        )

    elif res.status_code == 404:
        res_embed = discord.Embed(
            title="User not found",
            description="User `{0}` was not found.".format(username),
            color=0xFF0000
        )

    await ctx.send(embed=res_embed)


USER = os.getenv('GITBOT_DISCORD_KEY')
gitbot.run(USER)
