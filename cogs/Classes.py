import discord
import asyncio

from discord.ext import commands, menus
from discord.ext.commands import BucketType, cooldown, CommandOnCooldown

from Utilities import Checks, AssetCreation, PageSourceMaker

occupations = {
    'Soldier' : 'You are a retainer of a local lord, trained in the discipline of swordsmanship.\nYour base character ATK is boosted by 20% and you get a bonus 10 ATK.',
    'Blacksmith' : 'You\'ve spent years as the apprentice of a hardy blacksmith, and now a master in the art of forging.\nYour weapon ATK is boosted by 10% and you get a bonus 10 ATK.',
    'Farmer' : 'You are a lowly farmer, but farming is no easy job.\nYou gain increased resources from labor commands.',
    'Hunter' : 'The wild is your domain; no game unconquerable.\nYou gain double rewards from hunting.',
    'Merchant' : 'Screw you, exploiter of others\' labor.\nYou gain 50% increased income from selling items.',
    'Traveler' : 'The wild forests up north await, as do the raging seas to the south. What will you discover?\nYou gain triple gold from travel and double rewards from foraging.',
    'Leatherworker' : 'The finest protective gear, saddles, and equipment have your name on it.\nYou have 200 increased HP.',
    'Butcher' : 'Meat. What would one do without it?\nYou have double healing effectiveness.',
    'Engineer' : 'Your lord praises the seemingly impossible design of his new manor.\nYou will gain increased rewards from exclusive association commands.',
    'Scribe' : 'Despite the might of your lord, you\'ve learned a little bit about everything too.\nYou have an additional 10% crit rate.'
}

origins = {
    'Aramithea' : 'You\'re a metropolitan. Aramithea, the largest city on Rabidus, must have at least a million people, and a niche for everybody',
    'Riverburn' : 'The great rival of Aramithea; Will you bring your town to victory?',
    'Thenuille' : 'You love the sea; you love exploration; you love trade. From here one can go anywhere, and be anything',
    'Mythic Forest' : 'You come from the lands down south, covered in forest. You could probably hit a deer square between the eyes blindfolded.',
    'Sunset' : 'Nothing is more peaceful than an autumn afternoon in the prairie.',
    'Lunaris' : 'The crossroads of civilization; the battleground of those from the north, west, and east. Your times here have hardened you.',
    'Crumidia' : 'The foothills have turned you into a strong warrior. Perhaps you will seek domination over your adversaries?',
    'Maritimiala' : 'North of the mountains, the Maritimialan tribes look lustfully upon the fertile plains below. Will you seek integration, or domination?',
    'Glakelys' : 'The small towns beyond Riverburn disregard the Aramithean elite. The first line of defense from invasions from Lunaris, the Glakelys are as tribal as they were 300 years ago.'
}

occ = enumerate(occupations)
occ = list(occ)

# 0. Soldier - 15% bonus to character attack - implemented
# 1. Blacksmith - 10% bonus to weapon attack - implemented
# 2. Farmer - increased resources from labor commands
# 3. Hunter - double hunting rewards - implemented
# 4. Merchant - increased income from selling items - implemented
# 5. Traveler - triple travelling gold, double forage rewards - implemented
# 6. Leatherworker - increased HP (or DEF if added) - implemented
# 7. Butcher - increased healing effectiveness - implemented
# 8. Engineer - buff steal/invest slightly - implemented
# 9. Scribe - increased crit rate - implemented

ori = enumerate(origins)
ori = list(ori)

class Classes(commands.Cog):

    def __init__(self, client):
        self.client = client

    #EVENTS
    @commands.Cog.listener() # needed to create event in cog
    async def on_ready(self): # YOU NEED SELF IN COGS
        print('Classes is ready.')

    #COMMANDS
    @cooldown(1, 3600, BucketType.user)
    @commands.command(aliases=['class'], description='Choose your player class. This can be changed.')
    async def changeclass(self, ctx):
        entries = []
        for job in occupations:
            embed = discord.Embed(title='Class Selection Menu', color=0xBEDCF6)
            embed.add_field(name=f'{job}: Choose \u2705 to take this class!', value=f'{occupations[job]}')
            entries.append(embed)
        message = await ctx.reply(embed=entries[0])
        await message.add_reaction('\u23EE') #Left
        await message.add_reaction('\u2705') #Check
        await message.add_reaction('\u274E') #X
        await message.add_reaction('\u23ED') #Right

        def check(reaction, user):
            return user == ctx.author

        page = 0
        reaction = None
        readReactions = True

        while readReactions:
            if str(reaction) == '\u23EE':
                if page > 0:
                    page -= 1
                    await message.edit(embed=entries[page])
            if str(reaction) == '\u23ED':
                if page < 9:
                    page += 1
                    await message.edit(embed=entries[page])
            if str(reaction) == '\u274E':
                await message.delete()
                await ctx.send('No class chosen.')
                ctx.command.reset_cooldown(ctx)
                break
            if str(reaction) == '\u2705': # Then change class
                role = occ[page][1]
                await AssetCreation.setPlayerClass(self.client.pg_con, role, ctx.author.id)
                await ctx.send(f'{ctx.author.mention}, you are now a {role}!')
                await message.delete()
                break

            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60.0)
                await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                readReactions = not readReactions
                await message.delete()
        
    @commands.command(aliases=['background','birthplace'], description='Choose your birthplace.')
    async def origin(self, ctx):
        entries = []
        for place in origins:
            embed = discord.Embed(title='Background Selection Menu', color=0xBEDCF6)
            embed.add_field(name=f'{place}: Choose \u2705 if you like this place!', value=f'{origins[place]}')
            entries.append(embed)
        message = await ctx.reply(embed=entries[0])
        await message.add_reaction('\u23EE') #Left
        await message.add_reaction('\u2705') #Check
        await message.add_reaction('\u274E') #X
        await message.add_reaction('\u23ED') #Right

        def check(reaction, user):
            return user == ctx.author

        page = 0
        reaction = None
        readReactions = True

        while readReactions:
            if str(reaction) == '\u23EE':
                if page > 0:
                    page -= 1
                    await message.edit(embed=entries[page])
            if str(reaction) == '\u23ED':
                if page < 8:
                    page += 1
                    await message.edit(embed=entries[page])
            if str(reaction) == '\u274E':
                await message.delete()
                await ctx.send('Nothing chosen.')
                break
            if str(reaction) == '\u2705': # Then change class
                place = ori[page][1]
                await AssetCreation.setPlayerOrigin(self.client.pg_con, place, ctx.author.id)
                await ctx.send(f'{ctx.author.mention}, you are from {place}!')
                await message.delete()
                break

            try:
                reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=60.0)
                await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                readReactions = not readReactions
                await message.delete()

def setup(client):
    client.add_cog(Classes(client))