from app.models import CommandeGuild
from discord.ext import commands
from discord.ext.commands.bot import Bot 
from typing import Callable, Union
from app.constants import ApiConstant
import re

class CommandKarg:
    def __init__(self, name:str, required:bool = True, validation:Callable[[str],bool] = lambda value:True) -> None:
        self.name = name
        self.__validation = validation
        self.required = required

    def validate(self, value = None):
        error_message = None
        required = self.required and value == None
        valide = self.__validation(value) if value is not None else True
        try:
            if required:
                error_message = Message.command[ApiConstant.Errors.MISSING_REQUIRED_FIELD](self.name)
            elif not valide:
                error_message = Message.command[ApiConstant.Errors.INVALID_FIELD_VALUE](self.name)
        except Exception as e:
            print(e)
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
    command = {
        ApiConstant.Errors.FORBIDDEN: lambda command_name: f"Vous n'avez pas la permission d'exécuter la commande '{command_name}'",
        ApiConstant.Errors.NOT_FOUND: lambda command_name: f"La commande '{command_name}' n'existe pas",
        ApiConstant.Errors.MISSING_REQUIRED_FIELD: lambda command_name: f"Le champ '{command_name}' est requis",
        ApiConstant.Errors.INVALID_FIELD_VALUE: lambda command_name: f"Le champs '{command_name}' est invalide",
    }


class Command:
    def __init__(self, name:str, command_help:str,function: Callable[[commands.Context, any], Union[str, None]] = None, args: list[CommandKarg] = [], f_required: dict[str, Callable[['Command'], bool]] = {}):
        function = function if function else lambda ctx, **kwargs: None
        self.name:str = name
        self.args:list[CommandKarg] = args
        self.function:Callable[[commands.Context, any], Union[str, None]] = function
        self.commands:dict[str,Command] = {}
        self.f_required:dict[str, Callable[['Command'], bool]] = f_required
        self.help:str = command_help

    def add_command(self, command:'Command'):
        self.commands[command.name] = command

    async def run(self, ctx:commands.Context):
        message = ""
        content = re.sub(r'\s+', ' ', ctx.message.content)
        args:list[str] = content.split(' ')
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
            if not isinstance(value, list):
                value = [value]
            for current_value in value:
                for discord_command in command.args:
                    if discord_command.name == name:
                        error = None
                        if not discord_command.required:
                            required = self.f_required.get(discord_command.name, lambda command:False)(values)
                            if required:
                                if current_value is None:
                                    error = Message.command[ApiConstant.Errors.MISSING_REQUIRED_FIELD](discord_command.name)
                            else:
                                continue
                        if not error:
                            validation, error = discord_command.validate(current_value)
                        if error:
                            errors.append(error)
        if errors:
            return '\n'.join(errors)
        else:
            try:
                permissions = CommandeGuild.get_permission(command_path, ctx.guild.id)
                permission_user = [permission for permission in permissions if not permission.permission.startswith('<@&')]
                permission_role = [permission for permission in permissions if permission.permission.startswith('<@&')]
                allowed_permission_user = [permission.permission for permission in permission_user if permission.allow_permission]
                allowed_permission_role = [permission.permission for permission in permission_role if permission.allow_permission]
                denyed_permission_user = [permission.permission for permission in permission_user if not permission.allow_permission]
                denyed_permission_role = [permission.permission for permission in permission_role if not permission.allow_permission]
                
                user_roles = [role.mention  for role in ctx.author.roles]
                user_mention = ctx.author.mention
                allowed_user = True
                if any([role in user_roles for role in denyed_permission_role]):
                    allowed_user = False
                if any([role in user_roles for role in allowed_permission_role]):
                    allowed_user = True
                if user_mention in allowed_permission_user:
                    allowed_user = True
                if user_mention in denyed_permission_user:
                    allowed_user = False
                if ctx.guild.owner == ctx.author:
                    allowed_user = True

                if not allowed_user:
                    message = Message.command[ApiConstant.Errors.FORBIDDEN](command_path)
                else:
                    message = command.function(ctx, **values)
                # si coroutine, on attend le résultat
                if hasattr(message, '__await__'):
                    message = await message

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
            message = await self.run(ctx)
            if message:
                await ctx.send(message)
