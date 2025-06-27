A Discord bot made for friendly servers, aimed at providing useful extra features. 

# Features 
- Ask questions of the day that schedules and post them automatically, in a pre-configured channel
- Tell admin messages through bot DMs, useful for reporting users to admins
- Games (To be developed), such as wordle

# Deployment 
Visit [discord developer portal](https://discord.com/developers/applications):
- Create a new application
- Under the bot section, generate a new token and add to env variable `DISCORD_TOKEN`
- Go to oAuth2, check the `bot` and `applications.commands` scope
- Check `administrator` permissions
- Copy the invite link of the bot, and run `main.py()` with your token.
