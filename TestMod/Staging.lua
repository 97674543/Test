 
modimport("engine.lua") 
Load "chatinputscreen"
Load "consolescreen"
Load "textedit"
PrefabFiles = {
	"catbustempcat",
	"catbus_ball",
	"catbus_arrow",
	"reticuleline_test",
	"sample_sword",
	"sample_gun",
	"sample_projectile",
	"nekokan",
} 
Assets = {
    Asset( "IMAGE", "images/saveslot_portraits/catbustempcat.tex" ),
    Asset( "ATLAS", "images/saveslot_portraits/catbustempcat.xml" ), 
    Asset( "IMAGE", "images/selectscreen_portraits/catbustempcat.tex" ),
    Asset( "ATLAS", "images/selectscreen_portraits/catbustempcat.xml" ), 
    Asset( "IMAGE", "images/selectscreen_portraits/catbustempcat_silho.tex" ),
    Asset( "ATLAS", "images/selectscreen_portraits/catbustempcat_silho.xml" ), 
    Asset( "IMAGE", "bigportraits/catbustempcat.tex" ),
    Asset( "ATLAS", "bigportraits/catbustempcat.xml" ), 
	Asset( "IMAGE", "images/map_icons/catbustempcat.tex" ),
	Asset( "ATLAS", "images/map_icons/catbustempcat.xml" ), 
	Asset( "IMAGE", "images/avatars/avatar_catbustempcat.tex" ),
    Asset( "ATLAS", "images/avatars/avatar_catbustempcat.xml" ), 
	Asset( "IMAGE", "images/avatars/avatar_ghost_catbustempcat.tex" ),
    Asset( "ATLAS", "images/avatars/avatar_ghost_catbustempcat.xml" ), 
	Asset( "ATLAS", "images/hud/bombtab.xml" ),
	Asset( "IMAGE", "images/hud/bombtab.tex" ), 
	Asset("SOUNDPACKAGE", "sound/mettaton.fev"),
    Asset("SOUND", "sound/mettaton_bank00.fsb"), 
	Asset("SOUNDPACKAGE", "sound/hinozuki.fev"),
    Asset("SOUND", "sound/hinozuki_bank00.fsb"),
} 
local require = GLOBAL.require
local STRINGS = GLOBAL.STRINGS
local resolvefilepath = GLOBAL.resolvefilepath 
local Ingredient = GLOBAL.Ingredient
local RECIPETABS = GLOBAL.RECIPETABS
local Recipe = GLOBAL.Recipe
local TECH = GLOBAL.TECH 
local State = GLOBAL.State
local Action = GLOBAL.Action
local ActionHandler = GLOBAL.ActionHandler
local TimeEvent = GLOBAL.TimeEvent
local EventHandler = GLOBAL.EventHandler
local ACTIONS = GLOBAL.ACTIONS
local FRAMES = GLOBAL.FRAMES 
AddRecipe("sample_sword", 
{GLOBAL.Ingredient("nekokan", 1, "images/inventoryimages/nekokan.xml"),}, 
RECIPETABS.WAR, TECH.NONE, nil, nil, nil, nil, "catbustempcat", 
"images/inventoryimages/sample_sword.xml", "sample_sword.tex" ) 
AddRecipe("sample_gun", 
{GLOBAL.Ingredient("nekokan", 1, "images/inventoryimages/nekokan.xml"),}, 
RECIPETABS.WAR, TECH.NONE, nil, nil, nil, nil, "catbustempcat", 
"images/inventoryimages/sample_gun.xml", "sample_gun.tex" ) 
GLOBAL.STRINGS.NAMES.NEKOKAN = "Neko-kan"
GLOBAL.STRINGS.CHARACTERS.GENERIC.DESCRIBE.NEKOKAN = "Canned cat food."
GLOBAL.STRINGS.RECIPE_DESC.NEKOKAN = "Canned cat food!" 
GLOBAL.STRINGS.NAMES.SAMPLE_SWORD = "Fighter Sword"
GLOBAL.STRINGS.CHARACTERS.GENERIC.DESCRIBE.SAMPLE_SWORD = "It's a simple sword."
GLOBAL.STRINGS.RECIPE_DESC.SAMPLE_SWORD = "It's a simple sword." 
GLOBAL.STRINGS.NAMES.SAMPLE_GUN = "Gunslinger Gun"
GLOBAL.STRINGS.CHARACTERS.GENERIC.DESCRIBE.SAMPLE_GUN = "It's a simple gun."
GLOBAL.STRINGS.RECIPE_DESC.SAMPLE_GUN = "It's a simple gun." 
GLOBAL.STRINGS.ACTIONS.CASTAOE.SAMPLE_SWORD = "Catbus\n(-15 hunger)"
GLOBAL.STRINGS.ACTIONS.CASTAOE.SAMPLE_GUN = "Catbus\n(-15 hunger)" 
STRINGS.CHARACTER_TITLES.catbustempcat = "Sotai Neko"
STRINGS.CHARACTER_NAMES.catbustempcat = "Sotai Neko"
STRINGS.CHARACTER_DESCRIPTIONS.catbustempcat = "*Cat-bus nya!\n*.\n*."
STRINGS.CHARACTER_QUOTES.catbustempcat = "\"CAT BUSTERS!!\"" 
STRINGS.CHARACTERS.CATBUSTEMPCAT = require "speech_catbustempcat" 
STRINGS.NAMES.CATBUSTEMPCAT = "Neko" 
STRINGS.CHARACTERS.GENERIC.DESCRIBE.CATBUSTEMPCAT = 
{
	GENERIC = "It's Neko!",
	ATTACKER = "That Neko looks shifty...",
	MURDERER = "Murderer!",
	REVIVER = "Neko, friend of ghosts.",
	GHOST = "Neko could use a heart.",
} 
AddMinimapAtlas("images/map_icons/catbustempcat.xml") 
AddModCharacter("catbustempcat", "FEMALE") 
