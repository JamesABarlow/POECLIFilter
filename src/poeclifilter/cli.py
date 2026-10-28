from enum import StrEnum
from importlib.resources import files
from pprint import pprint

import questionary

import poeclifilter
from poeclifilter import game, loader
from poeclifilter.blocks import build_blocks
from poeclifilter.bootstrap import bootstrap_new_filter
from poeclifilter.filters import FilterRef, GameVersion
from poeclifilter.models import display_variables
from poeclifilter.models.banded_items import get_banded_items
from poeclifilter.renderer import render_filter
from poeclifilter.resources import list_filter_names


class Actions(StrEnum):
    CREATE_NEW_FILTER = "create_new_filter"
    RESET_FILTER_TO_DEFAULT = "reset_filter_to_default"
    BUILD_FILTER = "build_filter"


def ask_game_version() -> GameVersion | None:
    return questionary.select(
        "Which game?",
        choices=[
            questionary.Choice(title="Path of Exile 1", value=GameVersion.POE1),
            questionary.Choice(title="Path of Exile 2", value=GameVersion.POE2),
        ],
    ).ask()


def pick_filter_to_use(game_version: GameVersion) -> str:
    current_filters = list_filter_names(game_version)

    existing_filter_choices = []
    for current_filter in current_filters:
        existing_filter_choices.append(
            questionary.Choice(title=current_filter, value=current_filter)
        )

    # No existing filters, need to create a new one
    if not existing_filter_choices:
        print("No current filters found, creating new filter")
        choice = Actions.CREATE_NEW_FILTER
    else:
        choice = questionary.select(
            "Which filter to use?",
            choices=[
                *existing_filter_choices,
                questionary.Separator(),
                questionary.Choice(title="Create new filter", value=Actions.CREATE_NEW_FILTER),
            ],
        ).ask()

    if choice == Actions.CREATE_NEW_FILTER:
        return create_new_filter()
    else:
        return choice


def create_new_filter():
    new_filter_name = questionary.text("Enter name of new filter:").ask()
    # TODO: Actually bootstrap the new filter
    return new_filter_name


def top_level_filter_actions(filter_ref: FilterRef):
    # Edit, publish, reset to default, change filter
    choice = questionary.select(
        "What would you like to do?",
        choices=[
            questionary.Choice(title="Edit"),
            questionary.Choice(title="Build", value=Actions.BUILD_FILTER),
            questionary.Choice(
                title="Reset filter to default", value=Actions.RESET_FILTER_TO_DEFAULT
            ),
            questionary.Choice(title="Change filter"),
        ],
    ).ask()

    if choice == Actions.RESET_FILTER_TO_DEFAULT:
        bootstrap_new_filter(filter_ref)
    elif choice == Actions.BUILD_FILTER:
        render_filter(build_blocks(filter_ref))


def main():
    game_version = ask_game_version()
    if not game_version:
        return "game version not found"
    filter_name = pick_filter_to_use(game_version)

    filter_ref = FilterRef(game_version=game_version, name=filter_name)

    top_level_filter_actions(filter_ref)


if __name__ == "__main__":
    main()
