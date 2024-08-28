from app.models import Streamer, DiscordUser, User, CheckUser, DiscordStreamer, DiscordApp
from discord.ext import commands
from discord.ext.commands.bot import Bot 
from typing import Callable, Union
from app.constants import ApiConstant

class CommandKarg:
    def __init__(self, name:str, required:bool = True, validation:Callable[[str],bool] = lambda value:True) -> None:
        self.name = name
        self.__validation = validation
        self.required = required

    def validate(self, value = None):
        error_message = None
        required = self.required and value == None
        valide = self.__validation(value)
        if required:
            error_message = f"Le champs '{self.name}' est requis"
        elif not valide:
            error_message = f"Le champs '{self.name}' est invalide"
        return value == None and not self.required or self.__validation(value), error_message


class Message:
    streamer = {
        ApiConstant.Errors.NOT_FOUND: lambda streamer_name: f"Le streamer {streamer_name} n'existe pas",
        ApiConstant.Errors.NOT_FOUND_ON_TWITCH: lambda streamer_name: f"Le streamer {streamer_name} n'existe pas sur Twitch",
        ApiConstant.Errors.UNIQUE_CONSTRAINT_VIOLATION: lambda streamer_name: f"Le streamer {streamer_name} existe déjà",
        ApiConstant.Errors.MISSING_REQUIRED_FIELD: lambda streamer_name: f"Veuillez spécifier le nom du streamer",
        ApiConstant.Errors.SERVICE_UNAVAILIABLE: lambda streamer_name: f"Le service est indisponible n'est pas disponible",
        'added': lambda streamer_name: f"Le streamer {streamer_name} a été ajouté",
        'deleted': lambda streamer_name: f"Le streamer {streamer_name} a été supprimé",
        'updated': lambda streamer_name: f"Le streamer {streamer_name} a été mis à jour",
    }


class Command:
    def __init__(self, name:str, command_help:str,function: Callable[[commands.Context, any], Union[str, None]] = None, args: list[CommandKarg] = []):
        function = function if function else lambda ctx, **kwargs: None
        self.name:str = name
        self.args:list[CommandKarg] = args
        self.function:Callable[[commands.Context, any], Union[str, None]] = function
        self.commands:dict[str,Command] = {}
        self.help:str = command_help

    def add_command(self, command:'Command'):
        self.commands[command.name] = command

    def run(self, ctx:commands.Context):
        message = ""
        args:list[str] = ctx.message.content.split(' ')
        args.pop(0)
        errors:list[str] = []
        values:dict[str, list[str]] = {}

        command = self
        command_path = command.name

        while command.commands:
            if len(args) < 1:
                return f"Commandes disponibles: {', '.join(command.commands.keys())}"
            check_command = command.commands.get(args[0])
            if not check_command:
                return f"Commande inconnue\nCommandes disponibles: {', '.join(command.commands.keys())}"
            command = command.commands.get(args.pop(0))
            command_path += f" {command.name}"
            
        if len(command.args) > len(args):
            for _ in range(len(args), len(command.args)):
                args.append(None)

        for i, arg in enumerate(args):
            if len(command.args) > i + 1:
                values[command.args[i].name] = arg
            else:
                if len(command.args) == i + 1:
                    values[command.args[i].name] = [arg]
                else:
                    values[command.args[len(command.args)-1].name].append(arg)

        
        for name, value in values.items():
            for current_value in value:
                for arg in command.args:
                    if arg.name == name:
                        validation, error = arg.validate(current_value)
                        if error:
                            errors.append(error)
        if errors:
            return '\n'.join(errors)
        else:
            try:
                message = command.function(ctx, **values)
            except Exception as e:
                print(e)
                message = f"Une erreur est survenue dans la commande '{command_path}'"

        return message
        
    def add(self, bot:Bot):
        for command_name, command in self.commands.items():
            @bot.command(name=f"{self.name} {command_name}", help=command.help)
            async def _(ctx:commands.Context):
                return ""
                
        @bot.command(name=self.name, help=self.help)
        async def main_command(ctx:commands.Context):
            message = self.run(ctx)
            if message:
                await ctx.send(message)
class Permissions:
    def __init__(self, *roles) -> None:
        self.roles = roles

    def has_permission(self, user:User)->bool:
        return any([role in user.roles for role in self.roles])
