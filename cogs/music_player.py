import disnake
from disnake.ext import commands
from threading import Thread, Event



class MusicPlayer(Thread):
    def __init__(self):
        
        print()
