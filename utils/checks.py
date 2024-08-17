from disnake import ApplicationCommandInteraction
from disnake.ext.commands import check


def is_dev():
    devs = [
        1045011821838475334,
        397869855749177345,
    ]

    def predicate(inter: ApplicationCommandInteraction):
        return inter.author.id in devs

    return check(predicate)
