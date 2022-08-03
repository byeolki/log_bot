from nextcord import SlashOption, ChannelType
import nextcord, datetime, sqlite3, pytz
from nextcord.abc import GuildChannel
from nextcord.ext import commands

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix="접두사 입력란", intents=intents)

@client.event
async def on_ready():
    print(f"{client.user.name}봇은 준비가 완료 되었습니다.")
    print(f"[!] 참가 중인 서버 : {len(client.guilds)}개의 서버에 참여 중")
    print(f"[!] 이용자 수 : {len(client.users)}와 함께하는 중")

@client.slash_command(name="로그설정",description="특정채널에 로그를 기록하는 메세지를 보낼 수 있습니다")
async def hello(inter: nextcord.Interaction, 로그: str = SlashOption(description="무엇을 로깅할까요?", choices=["메세지 수정", "메세지 삭제", "음성채널"]), 채널: GuildChannel = SlashOption(description = "등록할 채널을 선택해주세요!",channel_types = [ChannelType.text])) -> None:
    if inter.user.guild_permissions.administrator:
        user = inter.user.id
        guild = inter.guild.id
        conn = sqlite3.connect("log.db", isolation_level=None)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS log(guild_id INTEGER, log TEXT, channel_id INTEGER)")
        c.execute("INSERT INTO log (guild_id, log, channel_id) VALUES (?, ?, ?)", (guild, 로그, 채널.id))
        embed = nextcord.Embed(title=f"로그 설정 성공!",color=0xd8b0cc,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.add_field(name=f"정보", value=f"이제부터 <#{채널.id}>의 {로그} 로그를 기록합니다!\n임베드는 기록하지 않습니다!", inline=True)
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        return await inter.response.send_message(embed=embed)
    await inter.send("관리자 권한이 필효합니다!")

@client.event
async def on_message_delete(message):
    if message.author == client:
        return None
    guild = message.guild.id
    conn = sqlite3.connect("log.db", isolation_level=None)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS log(guild_id INTEGER PRIMARY KEY, log TEXT, channel_id INTEGER)")
    if c.execute(f"SELECT * FROM log WHERE guild_id={guild} AND log='메세지 삭제'").fetchone() is not None:
        y = c.execute(f"SELECT * FROM log WHERE guild_id={guild} AND log='메세지 삭제'").fetchone()[-1]
        ch = client.get_channel(y)
        embed = nextcord.Embed(title=f"삭제가 감지됨됨", description=f"유저 : {message.author.mention} 채널 : {message.channel.mention}", color=0xd60505,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.add_field(name="삭제된 내용", value=f"```내용 : {message.content}```", inline=False)
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        await ch.send(embed=embed)

@client.event
async def on_message_edit(before, after):
    if after.author == client:
        return None
    guild = after.guild.id
    conn = sqlite3.connect("log.db", isolation_level=None)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS log(guild_id INTEGER PRIMARY KEY, log TEXT, channel_id INTEGER)")
    if c.execute(f"SELECT * FROM log WHERE guild_id={guild} AND log='메세지 수정'").fetchone() is not None:
        y = c.execute(f"SELECT * FROM log WHERE guild_id={guild} AND log='메세지 수정'").fetchone()[-1]
        ch = client.get_channel(y)
        embed = nextcord.Embed(title=f"수정이 감지됨", description=f"유저 : {before.author.mention} 채널 : {before.channel.mention}",  color=0xff9500,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.add_field(name="수정 전 내용", value=f"```{before.content}```", inline=True)
        embed.add_field(name="수정 후 내용", value=f"```{after.content}```", inline=True)
        embed.set_footer(text="Bot made by", icon_url="푸터 URL")
        await ch.send(embed=embed)

@client.event
async def on_voice_state_update(member, before, after):
    if member == client:
        return None
    else:
        guild = member.guild.id
        conn = sqlite3.connect("log.db", isolation_level=None)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS log(guild_id INTEGER PRIMARY KEY, log TEXT, channel_id INTEGER)")
        if c.execute(f"SELECT * FROM log WHERE guild_id={guild} AND log='음성채널'").fetchone() is not None:
            y = c.execute(f"SELECT * FROM log WHERE guild_id={guild} AND log='음성채널'").fetchone()[-1]
            ch = client.get_channel(y)
            if before.channel is None and after.channel is not None:
                embed = nextcord.Embed(title=f"음성채널에 입장이 감지됨", description=f"유저 : {member.mention}",  color=0xccff99,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
                embed.add_field(name="입장한 채널", value=f"<#{after.channel.id}>", inline=True)
                embed.set_footer(text="Bot made by", icon_url="푸터 URL")
                await ch.send(embed=embed)
            if before.channel is not None and after.channel is  None:
                embed = nextcord.Embed(title=f"음성채널에 퇴장이 감지됨", description=f"유저 : {member.mention}",  color=0xccff99,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
                embed.add_field(name="퇴장한 채널", value=f"<#{before.channel.id}>", inline=True)
                embed.set_footer(text="Bot made by", icon_url="푸터 URL")
                await ch.send(embed=embed)
            if before.channel is not None and after.channel is not None:
                embed = nextcord.Embed(title=f"음성채널에 이동이 감지됨", description=f"유저 : {member.mention}",  color=0xccff99,timestamp=datetime.datetime.now(pytz.timezone('UTC')))
                embed.add_field(name="퇴장한 채널", value=f"<#{before.channel.id}>", inline=True)
                embed.add_field(name="입장한 채널", value=f"<#{after.channel.id}>", inline=True)
                embed.set_footer(text="Bot made by", icon_url="푸터 URL")
                await ch.send(embed=embed)
                
client.run('토큰 입력란')
