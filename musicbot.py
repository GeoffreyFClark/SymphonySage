import nextcord
from nextcord.ext import commands
import nextwave
from nextwave.ext import spotify
from typing import Optional

DISCORD_TOKEN = 'YOUR DISCORD TOKEN HERE IN QUOTES'
SPOTIFY_CLIENT_ID = 'YOUR SPOTIFY CLIENT ID HERE'
SPOTIFY_CLIENT_SECRET = 'YOUR SPOTIFY CLIENT SECRET HERE'

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix='$', intents = intents, description='Premium quality music bot for free! <3')
setattr(nextwave.Player, 'lq', False)

bot.remove_command('help')
@bot.group(invoke_without_command=True)
async def help(ctx, helpstr: Optional[str] = None):
    user_commands = [play_command, spotifyplay_command, pause_command, resume_command, skip_command, clear_command, disconnect_command]
    if helpstr is not None:
        for i in user_commands:
            if i.name == helpstr:
                aliases = ' | '.join(list(i.aliases))
                embed = nextcord.Embed(description=f'**aliases**: {aliases}\n\n**function**: `{i.help}`\n\n**use**: {i.description}')
                await ctx.send(embed=embed)
    if helpstr is None:
        commands = ''.join(f'`${i.name}` ' for i in user_commands)
        help_description = f'{bot.description}\n**Commands:** {commands}\nType $help <command name> for more information about that command'
        embed = nextcord.Embed(title="Help", description=help_description)
        await ctx.send(embed=embed)

@commands.cooldown(1, 1, commands.BucketType.user)
@bot.command(name='play', aliases=['p'], help='play specified song', description='$p <song name>')
async def play_command(ctx: commands.Context, *, search:nextwave.YouTubeTrack):
    if not getattr(ctx.author.voice, 'channel', None):
        return await ctx.send(embed=nextcord.Embed(description='Try after joining voice channel'))
    elif not ctx.voice_client:
        vc: nextwave.Player = await ctx.author.voice.channel.connect(cls=nextwave.Player)
    else:
        vc: nextwave.Player = ctx.voice_client

    if vc.queue.is_empty and vc.is_playing() is False:   
        playString = await ctx.send(embed=nextcord.Embed(description='**searching...**'))
        await vc.play(search)
        await playString.edit(embed=nextcord.Embed(description=f'**Search found**\n\n`{search.title}`'))
    else:
        await vc.queue.put_wait(search)
        await ctx.send(embed=nextcord.Embed(description=f'Added to the `QUEUE`\n\n`{search.title}`'))
    vc.ctx = ctx  # [This is required for the on_nextwave_track_end event to work]

@commands.cooldown(1, 1, commands.BucketType.user)
@bot.command(name='splay', aliases=['sp'], help='play provided spotify playlist', description='$sp <spotify playlist link>')
async def spotifyplay_command(ctx: commands.Context, search: str):
    if not getattr(ctx.author.voice, 'channel', None):
        return await ctx.send(embed=nextcord.Embed(description='Try after joining voice channel'))
    elif not ctx.voice_client:
        vc: nextwave.Player = await ctx.author.voice.channel.connect(cls=nextwave.Player)
        await ctx.send(embed=nextcord.Embed(description='Spotify Playlist added to `QUEUE`'))
    else:
        vc: nextwave.Player = ctx.voice_client
        await ctx.send(embed=nextcord.Embed(description='Spotify Playlist added to `QUEUE`'))

    async for partial in spotify.SpotifyTrack.iterator(query=search, type=spotify.SpotifySearchType.playlist, partial_tracks=True):
        if vc.queue.is_empty and vc.is_playing() is False:
            await vc.play(partial)
        else:
            await vc.queue.put_wait(partial)
    vc.ctx = ctx 

@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='pause', aliases=['stop'], help='pauses current playing song', description='$pause')
async def pause_command(ctx: commands.Context):
    if await user_connectivity(ctx) == False:
        return
    vc: nextwave.Player = ctx.voice_client
    if vc._source:
        if not vc.is_paused():
            await vc.pause()
            await ctx.send(embed=nextcord.Embed(description='`PAUSED` the music!'))
        elif vc.is_paused():
            await ctx.send(embed=nextcord.Embed(description='Already `PAUSED`'))
    else:
        await ctx.send(embed=nextcord.Embed(description='Player is not `playing`!'))

@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='resume',aliases=[], help='resumes paused song', description='$resume')
async def resume_command(ctx: commands.Context):
    if await user_connectivity(ctx) == False:
        return
    vc: nextwave.Player = ctx.voice_client

    if vc.is_playing():
        if vc.is_paused():
            await vc.resume()
            await ctx.send(embed=nextcord.Embed(description='Music `RESUMED`!'))
        elif vc.is_playing():
            await ctx.send(embed=nextcord.Embed(description='Already `PLAYING`'))
    else:
        await ctx.send(embed=nextcord.Embed(description='Player is not `playing`!'))

@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='skip', aliases=['next', 's'], help='skips to next song', description='$s')
async def skip_command(ctx: commands.Context):
    if await user_connectivity(ctx) == False:
        return
    vc: nextwave.Player = ctx.voice_client
    if vc.queue.is_empty:
        await vc.stop()
        await vc.resume()
        return await ctx.send(embed=nextcord.Embed(description='Song stopped! No songs in `QUEUE`'))
    else:
        await vc.stop()
        vc.queue._wakeup_next()
        await vc.resume()
        return await ctx.send(embed=nextcord.Embed(description='`SKIPPED`!'))

@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='clear',aliases=[], help='clears the queue', description='$clear')
async def clear_command(ctx: commands.Context):
    vc: nextwave.Player = ctx.voice_client
    if await user_connectivity(ctx) == False:
        return
    if vc.queue.is_empty:
        return await ctx.send(embed= nextcord.Embed(description='No `SONGS` present'))
    vc.queue._queue.clear()
    clear_command_embed = nextcord.Embed(description='`QUEUE` cleared!')
    return await ctx.send(embed=clear_command_embed)

@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name='disconnect', aliases=['dc', 'leave'], help='disconnects the player from the vc', description='$dc')
async def disconnect_command(ctx: commands.Context):
    if await user_connectivity(ctx) == False:
        return
    vc : nextwave.Player = ctx.voice_client
    try:
        await vc.disconnect(force=True)
        await ctx.send(embed=nextcord.Embed(description='**BYE!** Have a great time!'))
    except Exception:
        await ctx.send(embed=nextcord.Embed(description='Failed to destroy!'))

@bot.event
async def on_ready():
    print(f'logged in as: {bot.user.name}')
    bot.loop.create_task(node_connect())
    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name="$help"))

@bot.event
async def on_nextwave_node_ready(node: nextwave.Node):
    print(f'Node {node.identifier} connected successfully')

async def node_connect():
    await bot.wait_until_ready()
    await nextwave.NodePool.create_node(bot=bot, host='lavalink.lexnet.cc', port=443, password="lexn3tl@val!nk", https=True, spotify_client=spotify.SpotifyClient(client_id=SPOTIFY_CLIENT_ID,client_secret=SPOTIFY_CLIENT_SECRET))

@bot.event
async def on_nextwave_track_end(player: nextwave.Player, track: nextwave.Track, reason):
    ctx = player.ctx
    vc: player = ctx.voice_client
    try:
        if not vc.queue.is_empty:
            next_song = vc.queue.get()
            await vc.play(next_song)
            await ctx.send(embed=nextcord.Embed(description=f'**Current song playing from the `QUEUE`**\n\n`{next_song.title}`'), delete_after=30)
    except Exception:
        await vc.stop()
        return await ctx.send(embed=nextcord.Embed(description='No songs in the `QUEUE`'))

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = nextcord.Embed(description=f'**Cooldown active**\ntry again in `{error.retry_after:.2f}`s*')
        await ctx.send(embed=em)
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=nextcord.Embed(description="Missing `arguments`"))
        return

async def user_connectivity(ctx: commands.Context):
    if not getattr(ctx.author.voice, 'channel', None):
        await ctx.send(embed=nextcord.Embed(description='Try after joining a `voice channel`',))
        return False
    return True

# Auto-disconnect if all participants leave the voice channel
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None:
        if bot.user in before.channel.members:
            if len(before.channel.members) == 1:
                for vc in bot.voice_clients:
                    if vc.channel == before.channel:
                        await vc.disconnect(force=True)
                        break
                        
if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
