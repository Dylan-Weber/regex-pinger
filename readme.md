# Discord Regex Pinger 

A simple Discord bot which lets you ping users and roles through regular expression matching!

Any user or role with a display name of the form /<regex>/ 

For example: A user with the display name "/foo|bar/" will be pinged by either "@foo" or "@bar". 

Pinging also works with emojis! A user with display name "/:emoji_name:/" will be pinged by "@:emoji_name:"

Messages are matched in a case insensitive manner, so "/display_name/" is pinged by "@display_name," "@Display_name," "@DISPLAY_NAME" or any other variant.