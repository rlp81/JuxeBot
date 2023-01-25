import discord
from discord.ext import commands
import wavelink
import configparser
import pafy

config = configparser.ConfigParser()
confile = config.read("config.conf")

# debug_guilds = [] input within discord.Bot() to use slash commands in select servers e.g. bot = discord.Bot(debug_guilds = [0000000000000000000, 11111111111111111111])
bot = discord.Bot()


class CustomPlayer(wavelink.Player):

    def __init__(self):

        super().__init__()

        self.queue = wavelink.Queue()


async def connect_nodes():

    await bot.wait_until_ready()

    await wavelink.NodePool.create_node(
        bot=bot,
        host='0.0.0.0',
        port=2333,
        password=config.get("config", "password")
    )


# COMMANDS


@bot.command(name="github")
async def github(ctx: commands.Context):

    await ctx.respond("Here's my github url: https://github.com/rlp81/JuxeBot")


@bot.command(name="queue", description="Lists queued songs")
async def queue(ctx: commands.Context):

    await ctx.defer()

    vc = ctx.voice_client

    if vc:

        if vc.queue.is_empty:

            return await ctx.respond("Nothing in queue.")

        else:

            emb = discord.Embed(title="Queue")

            num=0

            for i in vc.queue:

                num += 1

                emb.add_field(name=f"{num}",value=i,inline=False)

            await ctx.respond(embed=emb)

    else:

        return await ctx.respond("Bot not in a voice channel.")



@bot.command(name="ping", description="Returns ping of the bot")
async def ping(ctx: commands.Context):

    await ctx.respond(f"My ping is {round(len(bot.latency*1000))}")


@bot.command(name="pause", description="Pauses currently playing song")
async def pause(ctx: commands.Context):

    await ctx.defer()

    vc = ctx.voice_client

    if vc:

        if ctx.author.voice:

            if ctx.author.voice.channel.id == vc.channel.id:

                if not vc.is_playing():

                    return await ctx.respond("Nothing is playing")

                elif vc.is_playing():

                    await vc.pause()

                    await ctx.respond("Paused the song.")

                else:

                    if vc.is_paused():

                        return await ctx.respond("Bot is already paused.")

            else:

                return await ctx.respond("You must be in the same voice channel as the bot.")

        else:

            return await ctx.respond("You must be in a voice channel to run this command.")

    else:

        await ctx.respond("Bot is not in a voice channel.")



@bot.command(name="clear", description="Clears the queue")
async def clear(ctx: commands.Context):

    await ctx.defer()

    vc = ctx.voice_client

    if vc:

        if ctx.author.voice:

            if ctx.author.voice.channel.id == vc.channel.id:

                vc.queue.clear()

                await ctx.respond("Cleared the queue.")

            else:

                return await ctx.respond("You must be in the same voice channel as the bot.")

        else:

            return await ctx.respond("You must be in a voice channel to run this command.")


    else:
       return await ctx.respond("Bot is not in a channel.")



@bot.command(name="resume", description="Resumes currently paused song")
async def resume(ctx: commands.Context):

    await ctx.defer()

    vc = ctx.voice_client

    if vc:

        if ctx.author.voice:

            if ctx.author.voice.channel.id == vc.channel.id:

                if vc.is_playing():

                    return await ctx.respond("Bot is not paused.")

                else:

                    if vc.is_paused():

                        await vc.resume()

                        await ctx.respond("Resumed the bot.")

                    else:

                        return await ctx.respond("No songs are paused.")

            else:

                return await ctx.respond("You must be in the same voice channel as the bot.")

        else:

            return await ctx.respond("You must be in a voice channel to run this command.")

    else:

        await ctx.respond("Bot is not in a voice channel.")


@bot.command(name="skip", description="Skips currently playing song")
async def skip(ctx: commands.Context):

    await ctx.defer()

    vc = ctx.voice_client

    if vc:
        if ctx.author.voice:

            if ctx.author.voice.channel.id == vc.channel.id:
                if not vc.is_playing():

                    return await ctx.respond("Nothing is playing.")

                elif vc.queue.is_empty:

                    name = vc.source.title

                    await vc.stop()

                    await ctx.respond(f"Skipped song {name}")

                else:

                    name = vc.source.title

                    await ctx.respond(f"Skipped song {name}")

                    await vc.stop()

                    if vc.is_paused():

                        await vc.resume()

            else:

                return await ctx.respond("You must be in the same voice channel as the bot.")

        else:

            return await ctx.respond("You must be in a voice channel to run this command.")


    else:

        await ctx.respond("The bot is not connected to a voice channel.")


@bot.command(name="stop", description="Stops the music")
async def stop(ctx: commands.Context):

    await ctx.defer()

    vc = ctx.voice_client

    if not vc:

        return await ctx.respond("Bot not in voice channel.")

    else:
        if ctx.author.voice:

            if ctx.author.voice.channel.id == vc.channel.id:

                if vc.is_playing():

                    await ctx.respond(f"Stopped song {vc.source.title}")

                    vc.queue.clear()

                    await vc.stop()

                elif vc.is_paused():

                    vc.queue.clear()

                    await vc.stop()

                else:

                    return ctx.respond("Bot is not playing anything.")
            else:

                return await ctx.respond("You must be in the same voice channel as the bot.")

        else:

            return await ctx.respond("You must be in a voice channel to run this command.")


@bot.command(name="disconnect", description="Leaves the current channel")
async def disconnect(ctx: commands.Context):

    await ctx.defer()

    vc = ctx.voice_client

    if not vc:

        return await ctx.respond("Bot is not in a channel.")

    elif vc.channel.id != ctx.author.voice.channel.id:

        return await ctx.respond("You must be in the same channel as the bot.")

    else:

        await vc.disconnect()

        await ctx.respond("Disconnected from voice channel.")


@bot.command(name="connect", description="Connects to your channel")
async def connect(ctx: commands.Context):

    await ctx.defer()

    vc = ctx.voice_client

    if not vc:

        if ctx.author.voice:

            player = CustomPlayer()

            vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=player)

            await ctx.respond(f"Connected to voice channel {ctx.author.voice.channel.mention}")

        else:

            return await ctx.respond("You must be in a voice channel.")

    else:

        return await ctx.respond("Bot already in a channel.")


@bot.command(name="play", description="plays a song from youtube")
async def play(ctx: commands.Context, search: str):

    await ctx.defer()

    vc = ctx.voice_client

    if not vc:

        player = CustomPlayer()

        vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=player)

        song = await wavelink.YouTubeTrack.search(query=search, return_first=True)

        if not song:

            return await ctx.respond("No song was found.")

        await vc.play(song)

        if vc.source.uri:

            emb = discord.Embed(title=f"**{vc.source.title}**",
                                description=f"**Uploaded by:** {vc.source.info['author']}",
                                url=vc.source.uri
                                )

            thumb = pafy.new(vc.source.uri)

            value = thumb.bigthumb

            emb.set_thumbnail(url=value)

        else:

            emb = discord.Embed(title=f"**{vc.source.title}**",
                                description=f"**Uploaded by:** {vc.source.info['author']}"
                                )

        emb.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)

        await ctx.respond(embed=emb)

    elif ctx.author.voice.channel.id != vc.channel.id:

        return await ctx.respond("You must be in the same channel as the bot.")

    elif vc.is_playing():

        song = await wavelink.YouTubeTrack.search(query=search, return_first=True)

        if not song:

            return await ctx.respond("No song was found.")

        vc.queue.put(item=song)

        if song.uri:

            emb = discord.Embed(title=f"Queued **{song.title}**",
                                description=f"**Uploaded by:** {song.info['author']}",
                                url=song.uri
                                )

            thumb = pafy.new(song.uri)

            value = thumb.bigthumb

            emb.set_thumbnail(url=value)

            emb.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)

            await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(title=f"**{song.title}**",
                                description=f"**Uploaded by:** {song.info['author']}"
                                )

            await ctx.respond(embed=emb)


# EVENTS


@bot.event
async def on_wavelink_track_end(player: CustomPlayer, track: wavelink.Track, reason):
    if not player.queue.is_empty:

        next_track = player.queue.get()

        await player.play(next_track)


@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):

    print(f"Node: {node.identifier} is ready.")


@bot.event
async def on_ready():

    print(f"{bot.user} is ready.")

    bot.loop.create_task(connect_nodes())


if __name__ == "__main__":

    bot.run(config.get("config", "token"))
