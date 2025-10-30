🧭 You are here: [Wiki home](https://github.com/MarechJ/hll_rcon_tool/wiki/Home) / Developer Guides / [HLL RCONv2 Commands](https://github.com/MarechJ/hll_rcon_tool/wiki/Developer‐Guides-‐-HLL-RCONv2-Commands)

## Table of Contents
- [Table of Contents](#table-of-contents)
- [Protocol](#protocol)
  * [Executing Commands](#executing-commands)
  * [Authorization](#authorization)
  * [Responses & Errors](#responses--errors)
  * [Platforms](#platforms)
  * [Factions & Roles](#factions--roles)
- [Commands](#commands)
  * [Server](#server)
    + [`GetBannedWords`](#getbannedwords)
    + [`SetWelcomeMessage`](#setwelcomemessage-message)
    + [`ServerBroadcast`](#serverbroadcast-message)
    + [`SetHighPingThreshold`](#sethighpingthreshold-ms)
    + [`SetIdleKickDuration`](#setidlekickduration-minutes)
    + [`SetMaxQueuedPlayers`](#setmaxqueuedplayers-num)
    + [`SetTeamSwitchCooldown`](#setteamswitchcooldown-minutes)
  * [Command Introspection](#command-introspection)
    + [`GetDisplayableCommands`](#getdisplayablecommands)
    + [`GetClientReferenceData`](#getclientreferencedata-command)
  * [Maps & Rotation](#maps--rotation)
    + [`GetServerInformation: maprotation`](#getserverinformation-maprotation)
    + [`GetServerInformation: mapsequence`](#getserverinformation-mapsequence)
    + [`ChangeMap`](#changemap-mapname)
    + [`AddMapToRotation`](#addmaptorotation-mapname-index)
    + [`RemoveMapFromRotation`](#removemapfromrotation-index)
    + [`AddMapToSequence`](#addmaptosequence-mapname-index)
    + [`RemoveMapFromSequence`](#removemapfromsequence-index)
    + [`MoveMapInSequence`](#movemapinsequence-currentindex-newindex)
    + [`SetMapShuffleEnabled`](#setmapshuffleenabled-enable)
    + [`SetSectorLayout`](#setsectorlayout-sector_1-sector_2-sector_3-sector_4-sector_5)
    + *(Helpers)* [`GetAvailableMaps`](#helper-getavailablemaps) · [`GetAvailableSectorNames`](#helper-getavailablesectornames)
  * [Players](#players)
    + [`GetServerInformation: players`](#getserverinformation-players)
    + [`GetServerInformation: player`](#getserverinformation-player)
    + [`MessagePlayer`](#messageplayer-playerid-message)
    + [`PunishPlayer`](#punishplayer-playerid-reason)
    + [`KickPlayer`](#kickplayer-playerid-reason)
    + [`TemporaryBanPlayer` / `PermanentBanPlayer`](#temporarybanplayer--permanentbanplayer)
    + [`RemoveTemporaryBan`](#removetemporaryban-playerid)
    + [`RemovePermanentBan`](#removepermanentban-playerid)
    + *(Helper)* [`UnbanPlayer`](#helper-unbanplayer)
    + [`ForceTeamSwitch`](#forceteamswitch-playerid-forcemode)
    + [`RemovePlayerFromPlatoon`](#removeplayerfromplatoon-playerid-reason)
    + [`DisbandPlatoon`](#disbandplatoon-teamindex-squadindex-reason)
  * [Admins & Permissions](#admins--permissions)
    + [`GetAdminGroups`](#getadmingroups)
    + [`GetAdminUsers`](#getadminusers)
    + [`AddAdmin`](#addadmin-playerid-admingroup-comment)
    + [`RemoveAdmin`](#removeadmin-playerid)
  * [Bans & VIP](#bans--vip)
    + [`GetPermanentBans`](#getpermanentbans)
    + [`GetTemporaryBans`](#gettemporarybans)
    + [`AddVip`](#addvip-playerid-description)
    + [`RemoveVip`](#removevip-playerid)
    + [`SetVipSlotCount`](#setvipslotcount-num)
  * [Auto-balance & Vote-kick](#auto-balance--vote-kick)
    + [`SetAutoBalanceEnabled`](#setautobalanceenabled-enable)
    + [`SetAutoBalanceThreshold`](#setautobalancethreshold-autobalancethreshold)
    + [`SetVoteKickEnabled`](#setvotekickenabled-enable)
    + [`ResetVoteKickThreshold`](#resetvotekickthreshold)
    + [`SetVoteKickThreshold`](#setvotekickthreshold-thresholdvalue)
  * [Match Rules](#match-rules)
    + [`SetMatchTimer` / `RemoveMatchTimer`](#setmatchtimer--removematchtimer)
    + [`SetWarmupTimer` / `RemoveWarmupTimer`](#setwarmuptimer--removewarmuptimer)
    + [`SetDynamicWeatherEnabled`](#setdynamicweatherenabled-mapid-enable)
  * [Logs](#logs)
    + [`GetAdminLog`](#getadminlog-logbacktracktime-filters)
- [Available Maps](#available-maps)
- [Map Orientation and Faction Mirroring](#map-orientation-and-faction-mirroring)
- [Available Weapons](#available-weapons)
  * [**Firearms**](#firearms)
  * [**Deployables**](#deployables)
  * [**Vehicles (Roadkills)**](#vehicles-roadkills)
  * [**Vehicles (Armament)**](#vehicles-armament)
    + [**M8 Greyhound**](#m8-greyhound)
    + [**Stuart M5A1**](#stuart-m5a1)
    + [**Sherman M4A3(75)W**](#sherman-m4a375w)
    + [**Sherman M4A3E2 "75mm"**](#sherman-m4a3e2-75mm)
    + [**Sherman M4A3E2 "76mm"**](#sherman-m4a3e2-76mm)
    + [**M3 Half-track**](#m3-half-track)
    + [**Sd.Kfz.234 Puma**](#sdkfz234-puma)
    + [**Sd.Kfz.121 Luchs**](#sdkfz121-luchs)
    + [**Sd.Kfz.161 Panzer IV**](#sdkfz161-panzer-iv)
    + [**Sd.Kfz.171 Panther**](#sdkfz171-panzer)
    + [**Sd.Kfz.181 Tiger 1**](#sdkfz181-tiger-1)
    + [**Sd.Kfz 251 Half-track**](#sdkfz-251-half-track)
    + [**BA-10**](#ba-10)
    + [**T70**](#t70)
    + [**T34/76**](#t3476)
    + [**IS-1**](#is-1)
    + [**Daimler**](#daimler)
    + [**Tetrarch**](#tetrarch)
    + [**M3 Stuart Honey**](#m3-stuart-honey)
    + [**Cromwell**](#cromwell)
    + [**Crusader Mk.III**](#crusader-mkiii)
    + [**Firefly**](#firefly)
    + [**Churchill Mk.III**](#churchill-mkiii)
    + [**Churchill Mk.VII**](#churchill-mkvii)
  * [**Commander Abilities**](#commander-abilities)
  * [**Removed Weapons**](#removed-weapons)
  * [**Bugged Weapon Names**](#bugged-weapon-names)
- [Loadouts](#loadouts)
- [JSON Schemas (Selected Responses)](#json-schemas-selected-responses)
- [Notes & Gotchas](#notes--gotchas)

## Protocol
HLL RCONv2 is a TCP-based protocol with explicit command versioning. Messages consist of a fixed protocol header followed by a JSON-encoded payload.

### Executing Commands
Each request has the shape:
```json
{
  "command": "CommandName",
  "version": 2,
  "body": { "ParamA": "Value", "ParamB": 123 }
}
```
- **command** — Exact command identifier.
- **version** — Must be `2` for RCONv2 endpoints documented here.
- **body** — Object with command parameters; may be `{}` if none.

### Authorization
Authentication is performed when establishing the RCON TCP connection (outside the command body). The initial ServerConnect and Login commands provide an access token, which must be included in all subsequent commands within the session for authorization. Tools like the hllrcon library handle this token inclusion automatically for convenience.

### Responses & Errors
Responses are JSON. When successful, the body structure matches the **Returns** section of each command below. Errors are surfaced as non-2xx statuses internally; some helpers here interpret specific status codes as *falsey outcomes* (see **Notes & Gotchas**).

### Platforms
Players can be on multiple platforms:
- `steam`, `epic`, `xbl`, `psn`, `ps5`, `xsx`

### Factions & Roles
Faction IDs:
- `0 GER` (Germany)
- `1 US` (United States)
- `2 SOV` (Soviet Union)
- `3 CW` (Commonwealth)
- `4 DAK` (Deutsches Afrikakorps)
- `5 B8A` (British 8th Army)
- `6 UNASSIGNED`

Role IDs and Properties:
- `0 Rifleman` (Type: Infantry, Squad Leader: False, Kill Combat Score: 3, Assist Combat Score: 2)
- `1 Assault` (Type: Infantry, Squad Leader: False, Kill Combat Score: 6, Assist Combat Score: 4)
- `2 Automatic Rifleman` (Type: Infantry, Squad Leader: False, Kill Combat Score: 6, Assist Combat Score: 4)
- `3 Medic` (Type: Infantry, Squad Leader: False, Kill Combat Score: 6, Assist Combat Score: 4)
- `4 Spotter` (Type: Recon, Squad Leader: True, Kill Combat Score: 6, Assist Combat Score: 4)
- `5 Support` (Type: Infantry, Squad Leader: False, Kill Combat Score: 6, Assist Combat Score: 4)
- `6 Machine Gunner` (Type: Infantry, Squad Leader: False, Kill Combat Score: 9, Assist Combat Score: 6)
- `7 Anti-Tank` (Type: Infantry, Squad Leader: False, Kill Combat Score: 9, Assist Combat Score: 6)
- `8 Engineer` (Type: Infantry, Squad Leader: False, Kill Combat Score: 9, Assist Combat Score: 6)
- `9 Officer` (Type: Infantry, Squad Leader: True, Kill Combat Score: 9, Assist Combat Score: 6)
- `10 Sniper` (Type: Recon, Squad Leader: False, Kill Combat Score: 6, Assist Combat Score: 4)
- `11 Crewman` (Type: Armor, Squad Leader: False, Kill Combat Score: 3, Assist Combat Score: 2)
- `12 Tank Commander` (Type: Armor, Squad Leader: True, Kill Combat Score: 9, Assist Combat Score: 6)
- `13 Commander` (Type: Commander, Squad Leader: True, Kill Combat Score: 12, Assist Combat Score: 8)

**Role Properties:**
- **Type**: Indicates the category of the role (`Infantry`, `Armor`, `Recon`, `Commander`).
- **Squad Leader**: Whether the role is exclusive to squad leaders (e.g., Commander, Officer, Tank Commander, Spotter).
- **Kill Combat Score**: Combat Effectiveness score gained when killing a player with this role.
- **Assist Combat Score**: Combat Effectiveness score gained when assisting in the kill of a player with this role (e.g., when a player you downed is killed by another).

**Note**: The `Kill Combat Score` and `Assist Combat Score` are relevant for RCON commands like `GetServerInformation: player`, which return player score data (`scoreData.cOMBAT`).

## Commands

### Server

#### `GetBannedWords`
List banned words currently configured.
**Request**
```json
{"command":"GetServerInformation","version":2,"body":{"Name":"bannedwords","Value":""}}
```
**Returns**
```json
{ "bannedWords": ["word1","word2", "..."] }
```

#### `SetWelcomeMessage <Message>`
Set/Update the welcome message (shown at deploy & on spawn).
**Request**
```json
{"command":"SetWelcomeMessage","version":2,"body":{"Message":"Welcome to our server!"}}
```
**Returns**
- `200 OK` with empty JSON body on success.
**Notes**
- Triggers a brief re-display to currently spawned players.

#### `ServerBroadcast <Message>`
Display a broadcast message top-left to all players.
**Request**
```json
{"command":"ServerBroadcast","version":2,"body":{"Message":"Server restart in 10 minutes"}}
```
**Returns**
- `200 OK` with empty JSON body on success.

#### `SetHighPingThreshold <Ms>`
Kick players whose ping exceeds threshold (0 disables).
**Request**
```json
{"command":"SetHighPingThreshold","version":2,"body":{"HighPingThresholdMs":180}}
```
**Returns**
- `200 OK` on success.

#### `SetIdleKickDuration <Minutes>`
Kick players after being idle for N minutes (0 disables).
**Request**
```json
{"command":"SetIdleKickDuration","version":2,"body":{"IdleTimeoutMinutes":15}}
```
**Returns**
- `200 OK` on success.

#### `SetMaxQueuedPlayers <Num>`
Set server-side queue capacity (0–6).
**Request**
```json
{"command":"SetMaxQueuedPlayers","version":2,"body":{"MaxQueuedPlayers":6}}
```
**Returns**
- `200 OK` on success.

#### `SetTeamSwitchCooldown <Minutes>`
Minimum delay before players can switch teams again.
**Request**
```json
{"command":"SetTeamSwitchCooldown","version":2,"body":{"TeamSwitchTimer":10}}
```
**Returns**
- `200 OK` on success.

### Command Introspection

#### `GetDisplayableCommands`
List commands recognized by the server.
**Request**
```json
{"command":"GetDisplayableCommands","version":2,"body":""}
```
**Returns**
```json
{ "entries": [ { "iD":"...", "friendlyName":"...", "isClientSupported":true }, ... ] }
```

#### `GetClientReferenceData <Command>`
Describe a command’s UI text, description, and parameter schema.
**Request**
```json
{"command":"GetClientReferenceData","version":2,"body":"SetSectorLayout"}
```
**Returns**
```json
{
  "name":"SetSectorLayout",
  "text":"Set Sector Layout",
  "description":"Immediately restarts the match with the given sector layout",
  "dialogueParameters":[
    {"type":"Combo","name":"Sector 1","iD":"Sector_1","displayMember":"...","valueMember":"..."},
    ...
  ]
}
```

### Maps & Rotation

#### `GetServerInformation: maprotation`
Get configured **rotation** (static order).
**Request**
```json
{"command":"GetServerInformation","version":2,"body":{"Name":"maprotation","Value":""}}
```
**Returns**
```json
{ "mAPS": [
  {"name":"...","gameMode":"Warfare","timeOfDay":"Day","iD":"utahbeach_warfare","position":1}
]}
```

#### `GetServerInformation: mapsequence`
Get current **sequence** (may be shuffled).
**Request**
```json
{"command":"GetServerInformation","version":2,"body":{"Name":"mapsequence","Value":""}}
```
**Returns**
- Same shape as **maprotation**.

#### `ChangeMap <MapName>`
Start a 60s countdown and load the target map (skips EoR).
**Request**
```json
{"command":"ChangeMap","version":2,"body":{"MapName":"utahbeach_warfare"}}
```
**Returns**
- `200 OK` on success.
**Notes**
- Not immediate; visible 60s countdown to players.

#### `AddMapToRotation <MapName> <Index>`
Insert a map into the rotation at position `Index` (1-based).
**Request**
```json
{"command":"AddMapToRotation","version":2,"body":{"MapName":"utahbeach_warfare","Index":3}}
```
**Returns**
- `200 OK` on success.

#### `RemoveMapFromRotation <Index>`
Remove map at `Index` from rotation.
**Request**
```json
{"command":"RemoveMapFromRotation","version":2,"body":{"Index":3}}
```
**Returns**
- `200 OK` on success.

#### `AddMapToSequence <MapName> <Index>`
Insert a map into the sequence (the actual next maps list).
**Request**
```json
{"command":"AddMapToSequence","version":2,"body":{"MapName":"utahbeach_warfare","Index":2}}
```
**Returns**
- `200 OK` on success.

#### `RemoveMapFromSequence <Index>`
Remove map at `Index` from sequence.
**Request**
```json
{"command":"RemoveMapFromSequence","version":2,"body":{"Index":2}}
```
**Returns**
- `200 OK` on success.

#### `MoveMapInSequence <CurrentIndex> <NewIndex>`
Reorder maps in the sequence.
**Request**
```json
{"command":"MoveMapInSequence","version":2,"body":{"CurrentIndex":5,"NewIndex":2}}
```
**Returns**
- `200 OK` on success.

#### `SetMapShuffleEnabled <Enable>`
Enable or disable shuffling of the **sequence**.
**Request**
```json
{"command":"SetMapShuffleEnabled","version":2,"body":{"Enable":true}}
```
**Returns**
- `200 OK` on success.

#### `SetSectorLayout <Sector_1> <Sector_2> <Sector_3> <Sector_4> <Sector_5>`
Immediately restarts the match with the specified sector layout.
**Request**
```json
{"command":"SetSectorLayout","version":2,"body":{
  "Sector_1":"...", "Sector_2":"...", "Sector_3":"...", "Sector_4":"...", "Sector_5":"..."
}}
```
**Returns**
- `200 OK` on success.
**Notes / Warning**
- Use [`GetClientReferenceData("SetSectorLayout")`](#getclientreferencedata-command) to list valid sector names (`dialogueParameters` with `Sector_#` combos).

#### *(Helper)* `GetAvailableMaps`
Enumerate all maps supported by server-side UI for rotation/sequence operations.
**How**
- Call [`GetClientReferenceData("AddMapToRotation")`](#getclientreferencedata-command), read parameter `MapName.valueMember` (comma-separated).

#### *(Helper)* `GetAvailableSectorNames`
Enumerate valid sector names for the **current map**.
**How**
- Call [`GetClientReferenceData("SetSectorLayout")`](#getclientreferencedata-command) and read `Sector_1..Sector_5.valueMember` lists.

### Players

#### `GetServerInformation: players`
Get detailed info for **all online players**.
**Request**
```json
{"command":"GetServerInformation","version":2,"body":{"Name":"players","Value":""}}
```
**Returns (excerpt)**
```json
{ "players":[{
  "name":"(WTH) Abu", "clanTag":"WTH", "iD":"7656...", "platform":"steam", "eosId":"...",
  "level":174, "team":1, "role":9, "platoon":"Able",
  "loadout":"NCO", "kills":5, "deaths":3,
  "scoreData":{"cOMBAT":50,"offense":0,"defense":40,"support":10},
  "worldPosition":{"x":1234.0,"y":5678.0,"z":90.0}
}]}
```

#### `GetServerInformation: player`
Get detailed info for **one player** by ID (UID).
**Request**
```json
{"command":"GetServerInformation","version":2,"body":{"Name":"player","Value":"7656119..."}}
```
**Returns**
- Same shape as single entry in **players** list.

#### `MessagePlayer <PlayerId> <Message>`
Show a top-right message box to a specific player.
**Request**
```json
{"command":"MessagePlayer","version":2,"body":{"PlayerId":"7656119...","Message":"Read the rules, please."}}
```
**Returns**
- `200 OK` on success.

#### `PunishPlayer <PlayerId> [Reason]`
Kill the player (optionally with a reason displayed).
**Request**
```json
{"command":"PunishPlayer","version":2,"body":{"PlayerId":"7656119...","Reason":"Teamkilling"}}
```
**Returns**
- `200 OK` on success; may be interpreted as **false** in tooling if server returns status `500` (player not alive / not present).
**Note**
- See **Notes & Gotchas** on boolean casting for `kill_player`.

#### `KickPlayer <PlayerId> <Reason>`
Kick a player with a displayed reason.
**Request**
```json
{"command":"KickPlayer","version":2,"body":{"PlayerId":"7656119...","Reason":"Language"}}
```
**Returns**
- `200 OK` on success; may be interpreted as **false** by tooling when status `400` (player not found / already gone).

#### `TemporaryBanPlayer` / `PermanentBanPlayer`
Ban player temporarily or permanently.
**Temporary Request**
```json
{"command":"TemporaryBanPlayer","version":2,"body":{
  "PlayerId":"7656119...","Duration":2,"Reason":"Toxicity","AdminName":"Some Admin"
}}
```
**Permanent Request**
```json
{"command":"PermanentBanPlayer","version":2,"body":{
  "PlayerId":"7656119...","Reason":"Cheating","AdminName":"Some Admin"
}}
```
**Returns**
- `200 OK` on success.

#### `RemoveTemporaryBan <PlayerId>`
Unban a **temporary** ban by player ID.
**Request**
```json
{"command":"RemoveTemporaryBan","version":2,"body":{"PlayerId":"7656119..."}}
```
**Returns**
- `200 OK` on success; tooling interprets status `400` as **false** (no temp ban).

#### `RemovePermanentBan <PlayerId>`
Unban a **permanent** ban by player ID.
**Request**
```json
{"command":"RemovePermanentBan","version":2,"body":{"PlayerId":"7656119..."}}
```
**Returns**
- `200 OK` on success; tooling interprets status `400` as **false** (no perma ban).

#### *(Helper)* `UnbanPlayer`
Convenience behavior: call both `RemoveTemporaryBan` and `RemovePermanentBan` and return `true` if either succeeded.

#### `ForceTeamSwitch <PlayerId> <ForceMode>`
Force a player to switch teams.
- `ForceMode`: `0` = **IMMEDIATE** (kills player if alive), `1` = **AFTER_DEATH**
**Request**
```json
{"command":"ForceTeamSwitch","version":2,"body":{"PlayerId":"7656119...","ForceMode":0}}
```
**Returns**
- `200 OK` on success; tooling interprets status `500` as **false** (could not switch).

#### `RemovePlayerFromPlatoon <PlayerId> <Reason>`
Remove a player from their current squad (shown a message).
**Request**
```json
{"command":"RemovePlayerFromPlatoon","version":2,"body":{"PlayerId":"7656119...","Reason":"AFK"}}
```
**Returns**
- `200 OK` on success.

#### `DisbandPlatoon <TeamIndex> <SquadIndex> <Reason>`
Disband an entire squad (team + squad index).
**Request**
```json
{"command":"DisbandPlatoon","version":2,"body":{"TeamIndex":1,"SquadIndex":0,"Reason":"No SL"}}
```
**Returns**
- `200 OK` on success.

### Admins & Permissions

#### `GetAdminGroups`
List admin groups configured in server’s `AdminPermissions.ini`.
**Request**
```json
{"command":"GetAdminGroups","version":2,"body":""}
```
**Returns**
```json
{ "groupNames":["senior","camera","moderator","..."] }
```

#### `GetAdminUsers`
List players with admin permissions (group & comment).
**Request**
```json
{"command":"GetAdminUsers","version":2,"body":""}
```
**Returns**
```json
{ "adminUsers":[{"userId":"7656...","group":"senior","comment":"(WTH) Abu"}, ...] }
```

#### `AddAdmin <PlayerId> <AdminGroup> <Comment>`
Grant admin permissions to a player.
**Request**
```json
{"command":"AddAdmin","version":2,"body":{"PlayerId":"7656...","AdminGroup":"senior","Comment":"Abu"}}
```
**Returns**
- `200 OK` on success.

#### `RemoveAdmin <PlayerId>`
Revoke admin permissions from a player.
**Request**
```json
{"command":"RemoveAdmin","version":2,"body":{"PlayerId":"7656..."}}
```
**Returns**
- `200 OK` on success.

### Bans & VIP

#### `GetPermanentBans`
List permanent bans.
**Request**
```json
{"command":"GetPermanentBans","version":2,"body":""}
```
**Returns**
```json
{ "banList":[{"userId":"7656...","userName":"...","timeOfBanning":"...","durationHours":0,"banReason":"...","adminName":"..."}] }
```

#### `GetTemporaryBans`
List temporary bans.
**Request**
```json
{"command":"GetTemporaryBans","version":2,"body":""}
```
**Returns**
- Same shape as **GetPermanentBans**, with non-zero `durationHours`.

#### `AddVip <PlayerId> <Description>`
Add a VIP entry.
**Request**
```json
{"command":"AddVip","version":2,"body":{"PlayerId":"7656...","Description":"Frequent donor"}}
```
**Returns**
- `200 OK` on success.

#### `RemoveVip <PlayerId>`
Remove a VIP entry.
**Request**
```json
{"command":"RemoveVip","version":2,"body":{"PlayerId":"7656..."}}
```
**Returns**
- `200 OK` on success.

#### `SetVipSlotCount <Num>`
Set number of reserved VIP queue slots (server-side reserve).
**Request**
```json
{"command":"SetVipSlotCount","version":2,"body":{"VipSlotCount":5}}
```
**Returns**
- `200 OK` on success.

### Auto-balance & Vote-kick

#### `SetAutoBalanceEnabled <Enable>`
Enable/disable auto-balance logic.
**Request**
```json
{"command":"SetAutoBalanceEnabled","version":2,"body":{"Enable":true}}
```
**Returns**
- `200 OK` on success.

#### `SetAutoBalanceThreshold <AutoBalanceThreshold>`
Set max allowed team size delta **without** blocking joins.
**Request**
```json
{"command":"SetAutoBalanceThreshold","version":2,"body":{"AutoBalanceThreshold":2}}
```
**Returns**
- `200 OK` on success.
**Note**
- Setting to `0` **does not** disable auto-balance; use `SetAutoBalanceEnabled` instead.

#### `SetVoteKickEnabled <Enable>`
Enable/disable vote-kick system.
**Request**
```json
{"command":"SetVoteKickEnabled","version":2,"body":{"Enable":true}}
```
**Returns**
- `200 OK` on success.

#### `ResetVoteKickThreshold`
Restore default threshold curve.
**Request**
```json
{"command":"ResetVoteKickThreshold","version":2,"body":""}
```
**Returns**
- `200 OK` on success.

#### `SetVoteKickThreshold <ThresholdValue>`
Define threshold curve as CSV pairs: `players,votes,players,votes,...`
**Request**
```json
{"command":"SetVoteKickThreshold","version":2,"body":{"ThresholdValue":"0,5,25,10,50,15"}}
```
**Returns**
- `200 OK` on success.

### Match Rules

#### `SetMatchTimer` / `RemoveMatchTimer`
Set or reset match duration **for a game mode** (future matches).
**Set**
```json
{"command":"SetMatchTimer","version":2,"body":{"GameMode":"Warfare","MatchLength":90}}
```
**Remove**
```json
{"command":"RemoveMatchTimer","version":2,"body":{"GameMode":"Offensive"}}
```
**Returns**
- `200 OK` on success.

#### `SetWarmupTimer` / `RemoveWarmupTimer`
Set or reset warmup duration **for a game mode** (future matches).
**Set**
```json
{"command":"SetWarmupTimer","version":2,"body":{"GameMode":"Skirmish","WarmupLength":5}}
```
**Remove**
```json
{"command":"RemoveWarmupTimer","version":2,"body":{"GameMode":"Warfare"}}
```
**Returns**
- `200 OK` on success.

#### `SetDynamicWeatherEnabled <MapId> <Enable>`
Toggle dynamic weather for a specific map (future matches; only where supported).
**Request**
```json
{"command":"SetDynamicWeatherEnabled","version":2,"body":{"MapId":"utahbeach","Enable":true}}
```
**Returns**
- `200 OK` on success.

### Logs

#### `GetAdminLog <LogBackTrackTime> [Filters]`
Admin activity / moderation log entries within last N **seconds**.
**Request**
```json
{"command":"GetAdminLog","version":2,"body":{"LogBackTrackTime":600,"Filters":"kick,ban"}}
```
**Returns**
```json
{ "entries":[ {"timestamp":"2025-08-30T20:51:02Z","message":"KICK: [...]"}, ... ] }
```
**Notes**
- `LogBackTrackTime` must be non-negative.
- `Filters` may be an empty string to include everything.

## Available Maps
> **NOTE:** Some maps (e.g., `hill400_warfare_night`) are only available in PTEs.
> **NOTE:** The `Query Name` column corresponds to the `tag` field used in the game's data configuration.

| Map Name | Query Name | Pretty Name* | Base | Gamemode | Environment | Attackers |
|-|-|-|-|-|-|-|
| `CAR_S_1944_Day_P_Skirmish` | `CAR` | CARENTAN Skirmish | Carentan | Skirmish | Day | |
| `CAR_S_1944_Dusk_P_Skirmish` | `CAR` | CARENTAN Skirmish | Carentan | Skirmish | Dusk | |
| `CAR_S_1944_Rain_P_Skirmish` | `CAR` | CARENTAN Skirmish | Carentan | Skirmish | Rain | |
| `carentan_offensive_ger` | `CAR` | CARENTAN Offensive | Carentan | Offensive | Day | GER |
| `carentan_offensive_us` | `CAR` | CARENTAN Offensive | Carentan | Offensive | Day | US |
| `carentan_warfare` | `CAR` | CARENTAN Warfare | Carentan | Warfare | Day | |
| `carentan_warfare_night` | `CAR` | CARENTAN NIGHT Warfare | Carentan | Warfare | Night | |
| `driel_offensive_ger` | `DRL` | DRIEL Offensive | Driel | Offensive | Day | GER |
| `driel_offensive_us` | `DRL` | DRIEL Offensive | Driel | Offensive | Day | GB |
| `driel_warfare` | `DRL` | DRIEL Warfare | Driel | Warfare | Dawn | |
| `driel_warfare_night` | `DRL` | DRIEL Warfare | Driel | Warfare | Night | |
| `DRL_S_1944_P_Skirmish` | `DRL` | DRIEL Skirmish | Driel | Skirmish | Dawn | |
| `DRL_S_1944_Day_P_Skirmish` | `DRL` | DRIEL Skirmish | Driel | Skirmish | Day | |
| `DRL_S_1944_Night_P_Skirmish` | `DRL` | DRIEL Skirmish | Driel | Skirmish | Night | |
| `ELA_S_1942_P_Skirmish` | `ELA` | EL ALAMEIN Skirmish | El Alamein | Skirmish | Day | |
| `ELA_S_1942_Night_P_Skirmish` | `ELA` | EL ALAMEIN Skirmish | El Alamein | Skirmish | Dusk | |
| `elalamein_offensive_CW` | `ELA` | EL ALAMEIN Offensive | El Alamein | Offensive | Day | B8A |
| `elalamein_offensive_ger` | `ELA` | EL ALAMEIN Offensive | El Alamein | Offensive | Day | DAK |
| `elalamein_warfare` | `ELA` | EL ALAMEIN Warfare | El Alamein | Warfare | Day | |
| `elalamein_warfare_night` | `ELA` | EL ALAMEIN Warfare | El Alamein | Warfare | Dusk | |
| `elsenbornridge_offensiveger_day` | `EBR` | ELSENBORN RIDGE Offensive | Elsenborn Ridge | Offensive | Day | GER |
| `elsenbornridge_offensiveger_morning` | `EBR` | ELSENBORN RIDGE Offensive | Elsenborn Ridge | Offensive | Dawn | GER |
| `elsenbornridge_offensiveger_night` | `EBR` | ELSENBORN RIDGE Offensive | Elsenborn Ridge | Offensive | Night | GER |
| `elsenbornridge_offensiveUS_day` | `EBR` | ELSENBORN RIDGE Offensive | Elsenborn Ridge | Offensive | Day | US |
| `elsenbornridge_offensiveUS_morning` | `EBR` | ELSENBORN RIDGE Offensive | Elsenborn Ridge | Offensive | Dawn | US |
| `elsenbornridge_offensiveUS_night` | `EBR` | ELSENBORN RIDGE Offensive | Elsenborn Ridge | Offensive | Night | US |
| `elsenbornridge_skirmish_day` | `EBR` | ELSENBORN RIDGE Skirmish | Elsenborn Ridge | Skirmish | Day | |
| `elsenbornridge_skirmish_morning` | `EBR` | ELSENBORN RIDGE Skirmish | Elsenborn Ridge | Skirmish | Dawn | |
| `elsenbornridge_skirmish_night` | `EBR` | ELSENBORN RIDGE Skirmish | Elsenborn Ridge | Skirmish | Night | |
| `elsenbornridge_warfare_day` | `EBR` | ELSENBORN RIDGE Warfare | Elsenborn Ridge | Warfare | Day | |
| `elsenbornridge_warfare_morning` | `EBR` | ELSENBORN RIDGE Warfare | Elsenborn Ridge | Warfare | Dawn | |
| `elsenbornridge_warfare_night` | `EBR` | ELSENBORN RIDGE Warfare | Elsenborn Ridge | Warfare | Night | |
| `foy_offensive_ger` | `FOY` | FOY Offensive | Foy | Offensive | Day | GER |
| `foy_offensive_us` | `FOY` | FOY Offensive | Foy | Offensive | Day | US |
| `foy_warfare` | `FOY` | FOY Warfare | Foy | Warfare | Day | |
| `foy_warfare_night` | `FOY` | FOY Warfare | Foy | Warfare | Night | |
| `HIL_S_1944_Day_P_Skirmish` | `HIL` | HILL 400 Skirmish | Hill 400 | Skirmish | Day | |
| `HIL_S_1944_Dusk_P_Skirmish` | `HIL` | HILL 400 Skirmish | Hill 400 | Skirmish | Dusk | |
| `hill400_offensive_ger` | `HIL` | HILL 400 Offensive | Hill 400 | Offensive | Foggy | GER |
| `hill400_offensive_US` | `HIL` | HILL 400 Offensive | Hill 400 | Offensive | Day | US |
| `hill400_warfare` | `HIL` | HILL 400 Warfare | Hill 400 | Warfare | Day | |
| `hill400_warfare_night` | `HIL` | HILL 400 Warfare | Hill 400 | Warfare | Night | |
| `hurtgenforest_offensive_ger` | `HUR` | HÜRTGEN FOREST Offensive | Hürtgen Forest | Offensive | Foggy | GER |
| `hurtgenforest_offensive_US` | `HUR` | HÜRTGEN FOREST Offensive | Hürtgen Forest | Offensive | Day | US |
| `hurtgenforest_warfare_V2` | `HUR` | HÜRTGEN FOREST Warfare | Hürtgen Forest | Warfare | Day | |
| `hurtgenforest_warfare_V2_night` | `HUR` | HÜRTGEN FOREST Warfare | Hürtgen Forest | Warfare | Night | |
| `kharkov_offensive_ger` | `KHA` | Kharkov Offensive | Kharkov | Offensive | Day | GER |
| `kharkov_offensive_rus` | `KHA` | Kharkov Offensive | Kharkov | Offensive | Day | RUS |
| `kharkov_warfare` | `KHA` | Kharkov Warfare | Kharkov | Warfare | Day | |
| `kharkov_warfare_night` | `KHA` | Kharkov Warfare | Kharkov | Warfare | Night | |
| `kursk_offensive_ger` | `KUR` | KURSK Offensive | Kursk | Offensive | Day | GER |
| `kursk_offensive_rus` | `KUR` | KURSK Offensive | Kursk | Offensive | Day | RUS |
| `kursk_warfare` | `KUR` | KURSK Warfare | Kursk | Warfare | Day | |
| `kursk_warfare_night` | `KUR` | KURSK Warfare | Kursk | Warfare | Night | |
| `mortain_offensiveger_day` | `MOR` | MORTAIN Offensive | Mortain | Offensive | Day | GER |
| `mortain_offensiveger_dusk` | `MOR` | MORTAIN Offensive | Mortain | Offensive | Dawn | GER |
| `mortain_offensiveger_overcast` | `MOR` | MORTAIN Offensive | Mortain | Offensive | Overcast | GER |
| `mortain_offensiveUS_day` | `MOR` | MORTAIN Offensive | Mortain | Offensive | Day | US |
| `mortain_offensiveUS_dusk` | `MOR` | MORTAIN Offensive | Mortain | Offensive | Dawn | US |
| `mortain_offensiveUS_overcast` | `MOR` | MORTAIN Offensive | Mortain | Offensive | Overcast | US |
| `mortain_skirmish_day` | `MOR` | MORTAIN Skirmish | Mortain | Skirmish | Day | |
| `mortain_skirmish_dusk` | `MOR` | MORTAIN Skirmish | Mortain | Skirmish | Dawn | |
| `mortain_skirmish_overcast` | `MOR` | MORTAIN Skirmish | Mortain | Skirmish | Overcast | |
| `mortain_warfare_day` | `MOR` | MORTAIN Warfare | Mortain | Warfare | Day | |
| `mortain_warfare_dusk` | `MOR` | MORTAIN Warfare | Mortain | Warfare | Dawn | |
| `mortain_warfare_overcast` | `MOR` | MORTAIN Warfare | Mortain | Warfare | Overcast | |
| `omahabeach_offensive_ger` | `OMA` | OMAHA BEACH Offensive | Omaha Beach | Offensive | Day | GER |
| `omahabeach_offensive_us` | `OMA` | OMAHA BEACH Offensive | Omaha Beach | Offensive | Day | US |
| `omahabeach_warfare` | `OMA` | OMAHA BEACH Warfare | Omaha Beach | Warfare | Day | |
| `omahabeach_warfare_night` | `OMA` | OMAHA BEACH Warfare | Omaha Beach | Warfare | Dusk | |
| `PHL_L_1944_OffensiveGER` | `PHL` | PURPLE HEART LANE Offensive | Purple Heart Lane | Offensive | Day | GER |
| `PHL_L_1944_OffensiveUS` | `PHL` | PURPLE HEART LANE Offensive | Purple Heart Lane | Offensive | Day | US |
| `PHL_L_1944_Warfare` | `PHL` | PURPLE HEART LANE Warfare | Purple Heart Lane | Warfare | Rain | |
| `PHL_S_1944_Rain_P_Skirmish` | `PHL` | PURPLE HEART LANE Skirmish | Purple Heart Lane | Skirmish | Rain | |
| `PHL_S_1944_Morning_P_Skirmish` | `PHL` | PURPLE HEART LANE Skirmish | Purple Heart Lane | Skirmish | Morning | |
| `PHL_S_1944_Night_P_Skirmish` | `PHL` | PURPLE HEART LANE Skirmish | Purple Heart Lane | Skirmish | Night | |
| `remagen_offensive_ger` | `REM` | REMAGEN Offensive | Remagen | Offensive | Foggy | GER |
| `remagen_offensive_us` | `REM` | REMAGEN Offensive | Remagen | Offensive | Day | US |
| `remagen_warfare` | `REM` | REMAGEN Warfare | Remagen | Warfare | Day | |
| `remagen_warfare_night` | `REM` | REMAGEN Warfare | Remagen | Warfare | Night | |
| `SMDM_S_1944_Day_P_Skirmish` | `SMDM` | ST MARIE DU MONT Skirmish | St. Marie Du Mont | Skirmish | Day | |
| `SMDM_S_1944_Rain_P_Skirmish` | `SMDM` | ST MARIE DU MONT Skirmish | St. Marie Du Mont | Skirmish | Rain | |
| `SMDM_S_1944_Night_P_Skirmish` | `SMDM` | ST MARIE DU MONT Skirmish | St. Marie Du Mont | Skirmish | Night | |
| `SME_S_1944_Day_P_Skirmish` | `SME` | SAINTE-MÈRE-ÉGLISE Skirmish | St. Mere Eglise | Warfare | Day | |
| `SME_S_1944_Morning_P_Skirmish` | `SME` | SAINTE-MÈRE-ÉGLISE Skirmish | St. Mere Eglise | Warfare | Dawn | |
| `SME_S_1944_Night_P_Skirmish` | `SME` | SAINTE-MÈRE-ÉGLISE Skirmish | St. Mere Eglise | Warfare | Night | |
| `stalingrad_offensive_ger` | `STA` | STALINGRAD Offensive | Stalingrad | Offensive | Day | GER |
| `stalingrad_offensive_rus` | `STA` | STALINGRAD Offensive | Stalingrad | Offensive | Day | RUS |
| `stalingrad_warfare` | `STA` | STALINGRAD Warfare | Stalingrad | Warfare | Day | |
| `stalingrad_warfare_night` | `STA` | STALINGRAD Warfare | Stalingrad | Warfare | Night | |
| `stmariedumont_off_ger` | `SMDM` | ST MARIE DU MONT OFFENSIVE | St. Marie Du Mont | Offensive | Day | GER |
| `stmariedumont_off_us` | `SMDM` | ST MARIE DU MONT OFFENSIVE | St. Marie Du Mont | Offensive | Day | US |
| `stmariedumont_warfare` | `SMDM` | ST MARIE DU MONT Warfare | St. Marie Du Mont | Warfare | Day | |
| `stmariedumont_warfare_night` | `SMDM` | ST MARIE DU MONT Warfare | St. Marie Du Mont | Warfare | Night | |
| `stmereeglise_offensive_ger` | `SME` | SAINTE-MÈRE-ÉGLISE Offensive | St. Mere Eglise | Offensive | Dawn | GER |
| `stmereeglise_offensive_us` | `SME` | SAINTE-MÈRE-ÉGLISE Offensive | St. Mere Eglise | Offensive | Day | US |
| `stmereeglise_warfare` | `SME` | SAINTE-MÈRE-ÉGLISE Warfare | St. Mere Eglise | Warfare | Day | |
| `stmereeglise_warfare_night` | `SME` | SAINTE-MÈRE-ÉGLISE Warfare | St. Mere Eglise | Warfare | Night | |
| `tobruk_offensiveger_day` | `TBK` | TOBRUK Offensive | Tobruk | Offensive | Day | DAK |
| `tobruk_offensiveger_morning` | `TBK` | TOBRUK Offensive | Tobruk | Offensive | Dawn | DAK |
| `tobruk_offensiveger_dusk` | `TBK` | TOBRUK Offensive | Tobruk | Offensive | Dusk | DAK |
| `tobruk_offensivebritish_day` | `TBK` | TOBRUK Offensive | Tobruk | Offensive | Day | B8A |
| `tobruk_offensivebritish_morning` | `TBK` | TOBRUK Offensive | Tobruk | Offensive | Dawn | B8A |
| `tobruk_offensivebritish_dusk` | `TBK` | TOBRUK Offensive | Tobruk | Offensive | Dusk | B8A |
| `tobruk_skirmish_day` | `TBK` | TOBRUK Skirmish | Tobruk | Skirmish | Day | |
| `tobruk_skirmish_morning` | `TBK` | TOBRUK Skirmish | Tobruk | Skirmish | Dawn | |
| `tobruk_skirmish_dusk` | `TBK` | TOBRUK Skirmish | Tobruk | Skirmish | Dusk | |
| `tobruk_warfare_day` | `TBK` | TOBRUK Warfare | Tobruk | Warfare | Day | |
| `tobruk_warfare_morning` | `TBK` | TOBRUK Warfare | Tobruk | Warfare | Dawn | |
| `tobruk_warfare_dusk` | `TBK` | TOBRUK Warfare | Tobruk | Warfare | Dusk | |
| `utahbeach_offensive_ger` | `UTA` | UTAH BEACH Offensive | Utah Beach | Offensive | Day | GER |
| `utahbeach_offensive_us` | `UTA` | UTAH BEACH Offensive | Utah Beach | Offensive | Day | US |
| `utahbeach_warfare` | `UTA` | UTAH BEACH Warfare | Utah Beach | Warfare | Day | |
| `utahbeach_warfare_night` | `UTA` | UTAH BEACH Warfare | Utah Beach | Warfare | Night | |

<sup>* Appears in `MATCH START` and `MATCH ENDED` logs.<br>** Lowercase in `Get Map` and `Get Gamestate` outputs.<br>*** Only in PTEs.

## Map Orientation and Faction Mirroring
Each map has an **orientation** and **mirror_factions** property that affects gameplay configuration:
- **Orientation**: Determines how sectors are arranged on the map:
  - `Horizontal`: Sectors are stacked left-to-right.
  - `Vertical`: Sectors are stacked top-to-bottom.
- **Mirror Factions**: Indicates whether faction spawn points are mirrored:
  - `False`: Allies spawn on the left (for Horizontal) or top (for Vertical), Axis spawn on the right (for Horizontal) or bottom (for Vertical).
  - `True`: Faction spawns are reversed (e.g., Axis on left/top, Allies on right/bottom).
These properties impact commands like `SetSectorLayout` and should be considered when configuring map rotations or sector layouts.

**Map Configurations**:
- **Carentan**: Horizontal, mirror_factions=False (Allies: US, Axis: GER)
- **Driel**: Vertical, mirror_factions=True (Allies: CW, Axis: GER)
- **El Alamein**: Horizontal, mirror_factions=True (Allies: B8A, Axis: DAK)
- **Elsenborn Ridge**: Vertical, mirror_factions=False (Allies: US, Axis: GER)
- **Foy**: Vertical, mirror_factions=True (Allies: US, Axis: GER)
- **Hill 400**: Horizontal, mirror_factions=False (Allies: US, Axis: GER)
- **Hürtgen Forest**: Horizontal, mirror_factions=False (Allies: US, Axis: GER)
- **Kharkov**: Vertical, mirror_factions=False (Allies: SOV, Axis: GER)
- **Kursk**: Vertical, mirror_factions=False (Allies: SOV, Axis: GER)
- **Mortain**: Horizontal, mirror_factions=False (Allies: US, Axis: GER)
- **Omaha Beach**: Horizontal, mirror_factions=True (Allies: US, Axis: GER)
- **Purple Heart Lane**: Vertical, mirror_factions=False (Allies: US, Axis: GER)
- **Remagen**: Vertical, mirror_factions=True (Allies: US, Axis: GER)
- **St. Marie Du Mont**: Vertical, mirror_factions=False (Allies: US, Axis: GER)
- **St. Mere Eglise**: Horizontal, mirror_factions=True (Allies: US, Axis: GER)
- **Stalingrad**: Horizontal, mirror_factions=True (Allies: SOV, Axis: GER)
- **Tobruk**: Horizontal, mirror_factions=True (Allies: B8A, Axis: DAK)
- **Utah Beach**: Horizontal, mirror_factions=True (Allies: US, Axis: GER)

## Available Weapons
> **NOTE**: The British melee weapon uses an "En Dash" (–) instead of a hyphen (-).

### Firearms
| Category | United States (US) | Germany (GER) | Soviet Union (RUS) | Great Britain (GB) |
|-|-|-|-|-|
| **Submachine Guns** | `M1A1 THOMPSON`, `M3 GREASE GUN` | `MP40` | `PPSH 41`, `PPSH 41 W/DRUM` | `Sten Gun Mk.II`, `Sten Gun Mk.V`, `Lanchester`, `M1928A1 THOMPSON` |
| **Semi-Auto Rifles** | `M1 GARAND`, `M1 CARBINE` | `GEWEHR 43` | `SVT40` | |
| **Bolt-Action Rifles** | | `KARABINER 98K` | `MOSIN NAGANT 1891`, `MOSIN NAGANT 91/30`, `MOSIN NAGANT M38` | `SMLE No.1 Mk III`, `Rifle No.4 Mk I`, `Rifle No.5 Mk I` |
| **Assault Rifles** | `M1918A2 BAR` | `STG44`, `FG42` | | `Bren Gun` |
| **Shotguns** | `M97 TRENCH GUN` | | | |
| **Machine Guns** | `BROWNING M1919` | `MG34`, `MG42` | `DP-27` | `Lewis Gun` |
| **Sniper Rifles** | `M1919 SPRINGFIELD` | `KARABINER 98K x8`, `FG42 x4` | `SCOPED MOSIN NAGANT 91/30`, `SCOPED SVT40` | `Lee-Enfield Pattern 1914 Sniper`, `Rifle No.4 Mk I Sniper` |
| **Pistols** | `COLT M1911` | `WALTHER P38`, `LUGER P08` | `NAGANT M1895`, `TOKAREV TT33` | `Webley MK VI` |
| **Flamethrowers** | `M2 FLAMETHROWER` | `FLAMMENWERFER 41` | | `FLAMETHROWER` |
| **Melee Weapons** | `M3 KNIFE` | `FELDSPATEN` | `MPL-50 SPADE` | `Fairbairn–Sykes` |
| **Grenades** | `MK2 GRENADE` | `M24 STIELHANDGRANATE`, `M43 STIELHANDGRANATE` | `RG-42 GRENADE`, `MOLOTOV` | `Mills Bomb`, `No.82 Grenade` |
| **Satchel Charges** | `SATCHEL` | `SATCHEL` | `SATCHEL CHARGE` | `Satchel` |
| **Anti-Personnel Mines** | `M2 AP MINE` | `S-MINE` | `POMZ AP MINE` | `A.P. Shrapnel Mine Mk II` |
| **Anti-Tank Mines** | `M1A1 AT MINE` | `TELLERMINE 43` | `TM-35 AT MINE` | `A.T. Mine G.S. Mk V` |
| **Anti-Tank Rifles** | `BAZOOKA` | `PANZERSCHRECK` | `PTRS-41`, `BAZOOKA` | `PIAT`, `Boys Anti-tank Rifle` |
| **Flare Guns** | `FLARE GUN` | `FLARE GUN` | `FLARE GUN` | `No.2 Mk 5 Flare Pistol` |

### Deployables
| Category | United States (US) | Germany (GER) | Soviet Union (RUS) | Great Britain (GB) |
|-|-|-|-|-|
| **Artillery Guns** | `155MM HOWITZER [M114]` | `150MM HOWITZER [sFH 18]` | `122MM HOWITZER [M1938 (M-30)]` | `QF 25-POUNDER [QF 25-Pounder]` |
| **Anti-Tank Guns** | `57MM CANNON [M1 57mm]` | `75MM CANNON [PAK 40]` | `57MM CANNON [ZiS-2]` | `QF 6-POUNDER [QF 6-Pounder]` |

### Vehicles (Roadkills)
| Category | United States (US) | Germany (GER) | Soviet Union (RUS) | Great Britain (GB) |
|-|-|-|-|-|
| **Recon Vehicles** | `M8 Greyhound` | `Sd.Kfz.234 Puma` | `BA-10` | `Daimler` |
| **Light Tanks** | `Stuart M5A1` | `Sd.Kfz.121 Luchs` | `T70` | `Tetrarch`, `M3 Stuart Honey` |
| **Medium Tanks** | `Sherman M4A3(75)W` | `Sd.Kfz.161 Panzer IV` | `T34/76` | `Cromwell`, `Crusader Mk.III` |
| **Heavy Tanks** | `Sherman M4A3E2`, `Sherman M4A3E2(76)` | `Sd.Kfz.181 Tiger 1`, `Sd.Kfz.171 Panther` | `IS-1` | `Firefly`, `Churchill Mk.III`, `Churchill Mk.VII` |
| **Half-tracks** | `M3 Half-track` | `Sd.Kfz 251 Half-track` | `M3 Half-track` | `M3 Half-track` |
| **Trucks** | `GMC CCKW 353 (Transport)`, `GMC CCKW 353 (Supply)` | `Opel Blitz (Transport)`, `Opel Blitz (Supply)` | `ZIS-5 (Transport)`, `ZIS-5 (Supply)` | `Bedford OYD (Transport)`, `Bedford OYD (Supply)` |
| **Jeeps** | `Jeep Willys` | `Kubelwagen` | `GAZ-67` | `Jeep Willys` |

### Vehicles (Armament)
> **NOTE**: If a vehicle is destroyed, post-destruction kills omit the vehicle name (e.g., `COAXIAL M1919 [M8 Greyhound]` becomes `COAXIAL M1919`).

#### M8 Greyhound
Recon Vehicle - United States (US)
| Category | Name |
|-|-|
| **Main Cannon** | `M6 37mm [M8 Greyhound]` |
| **Coaxial Machine Gun** | `COAXIAL M1919 [M8 Greyhound]` |

#### Stuart M5A1
Light Tank - United States (US)
| Category | Name |
|-|-|
| **Main Cannon** | `37MM CANNON [Stuart M5A1]` |
| **Coaxial Machine Gun** | `COAXIAL M1919 [Stuart M5A1]` |
| **Hull Machine Gun** | `HULL M1919 [Stuart M5A1]` |

#### Sherman M4A3(75)W
Medium Tank - United States (US)
| Category | Name |
|-|-|
| **Main Cannon** | `75MM CANNON [Sherman M4A3(75)W]` |
| **Coaxial Machine Gun** | `COAXIAL M1919 [Sherman M4A3(75)W]` |
| **Hull Machine Gun** | `HULL M1919 [Sherman M4A3(75)W]` |

#### Sherman M4A3E2 "75mm"
Heavy Tank - United States (US)
| Category | Name |
|-|-|
| **Main Cannon** | `75MM M3 GUN [Sherman M4A3E2]` |
| **Coaxial Machine Gun** | `COAXIAL M1919 [Sherman M4A3E2]` |
| **Hull Machine Gun** | `HULL M1919 [Sherman M4A3E2]` |

#### Sherman M4A3E2 "76mm"
Heavy Tank - United States (US)
| Category | Name |
|-|-|
| **Main Cannon** | `76MM M1 GUN [Sherman M4A3E2(76)]` |
| **Coaxial Machine Gun** | `COAXIAL M1919 [Sherman M4A3E2(76)]` |
| **Hull Machine Gun** | `HULL M1919 [Sherman M4A3E2(76)]` |

#### M3 Half-track
Half-track - United States (US), Soviet Union (RUS) & Great Britain (GB)
| Category | Name |
|-|-|
| **Mounted Machine Gun** | `M2 Browning [M3 Half-track]` |

#### Sd.Kfz.234 Puma
Recon Vehicle - Germany (GER)
| Category | Name |
|-|-|
| **Main Cannon** | `50mm KwK 39/1 [Sd.Kfz.234 Puma]` |
| **Coaxial Machine Gun** | `COAXIAL MG34 [Sd.Kfz.234 Puma]` |

#### Sd.Kfz.121 Luchs
Light Tank - Germany (GER)
| Category | Name |
|-|-|
| **Main Cannon** | `20MM KWK 30 [Sd.Kfz.121 Luchs]` |
| **Coaxial Machine Gun** | `COAXIAL MG34 [Sd.Kfz.121 Luchs]` |

#### Sd.Kfz.161 Panzer IV
Medium Tank - Germany (GER)
| Category | Name |
|-|-|
| **Main Cannon** | `75MM CANNON [Sd.Kfz.161 Panzer IV]` |
| **Coaxial Machine Gun** | `COAXIAL MG34 [Sd.Kfz.161 Panzer IV]` |
| **Hull Machine Gun** | `HULL MG34 [Sd.Kfz.161 Panzer IV]` |

#### Sd.Kfz.171 Panther
Heavy Tank - Germany (GER)
| Category | Name |
|-|-|
| **Main Cannon** | `75MM CANNON [Sd.Kfz.171 Panther]` |
| **Coaxial Machine Gun** | `COAXIAL MG34 [Sd.Kfz.171 Panther]` |
| **Hull Machine Gun** | `HULL MG34 [Sd.Kfz.171 Panther]` |

#### Sd.Kfz.181 Tiger 1
Heavy Tank - Germany (GER)
| Category | Name |
|-|-|
| **Main Cannon** | `88 KWK 36 L/56 [Sd.Kfz.181 Tiger 1]` |
| **Coaxial Machine Gun** | `COAXIAL MG34 [Sd.Kfz.181 Tiger 1]` |
| **Hull Machine Gun** | `HULL MG34 [Sd.Kfz.181 Tiger 1]` |

#### Sd.Kfz 251 Half-track
Half-track - Germany (GER)
| Category | Name |
|-|-|
| **Mounted Machine Gun** | `MG 42 [Sd.Kfz 251 Half-track]` |

#### BA-10
Recon Vehicle - Soviet Union (RUS)
| Category | Name |
|-|-|
| **Main Cannon** | `19-K 45MM [BA-10]` |
| **Coaxial Machine Gun** | `COAXIAL DT [BA-10]` |

#### T70
Light Tank - Soviet Union (RUS)
| Category | Name |
|-|-|
| **Main Cannon** | `45MM M1937 [T70]` |
| **Coaxial Machine Gun** | `COAXIAL DT [T70]` |

#### T34/76
Medium Tank - Soviet Union (RUS)
| Category | Name |
|-|-|
| **Main Cannon** | `76MM ZiS-5 [T34/76]` |
| **Coaxial Machine Gun** | `COAXIAL DT [T34/76]` |
| **Hull Machine Gun** | `HULL DT [T34/76]` |

#### IS-1
Heavy Tank - Soviet Union (RUS)
| Category | Name |
|-|-|
| **Main Cannon** | `D-5T 85MM [IS-1]` |
| **Coaxial Machine Gun** | `COAXIAL DT [IS-1]` |
| **Hull Machine Gun** | `HULL DT [IS-1]` |

#### Daimler
Recon Vehicle - Great Britain (GB)
| Category | Name |
|-|-|
| **Main Cannon** | `QF 2-POUNDER [Daimler]` |
| **Coaxial Machine Gun** | `COAXIAL BESA [Daimler]` |

#### Tetrarch
Light Tank - Great Britain (GB)
| Category | Name |
|-|-|
| **Main Cannon** | `QF 2-POUNDER [Tetrarch]` |
| **Coaxial Machine Gun** | `COAXIAL BESA [Tetrarch]` |

#### M3 Stuart Honey
Light Tank - Great Britain (GB)
| Category | Name |
|-|-|
| **Main Cannon** | `37MM CANNON [M3 Stuart Honey]` |
| **Coaxial Machine Gun** | `COAXIAL M1919 [M3 Stuart Honey]` |
| **Hull Machine Gun** | `HULL M1919 [M3 Stuart Honey]` |

#### Cromwell
Medium Tank - Great Britain (GB)
| Category | Name |
|-|-|
| **Main Cannon** | `OQF 75MM [Cromwell]` |
| **Coaxial Machine Gun** | `COAXIAL BESA [Cromwell]` |
| **Hull Machine Gun** | `HULL BESA [Cromwell]` |

#### Crusader Mk.III
Medium Tank - Great Britain (GB)
| Category | Name |
|-|-|
| **Main Cannon** | `OQF 57MM [Crusader Mk.III]` |
| **Coaxial Machine Gun** | `COAXIAL BESA [Crusader Mk.III]` |

#### Firefly
Heavy Tank - Great Britain (GB)
| Category | Name |
|-|-|
| **Main Cannon** | `QF 17-POUNDER [Firefly]` |
| **Coaxial Machine Gun** | `COAXIAL M1919 [Firefly]` |

#### Churchill Mk.III
Heavy Tank - Great Britain (GB)
| Category | Name |
|-|-|
| **Main Cannon** | `OQF 57MM [Churchill Mk.III]` |
| **Coaxial Machine Gun** | `COAXIAL BESA 7.92mm [Churchill Mk.III]` |
| **Hull Machine Gun** | `HULL BESA 7.92mm [Churchill Mk.III]` |

#### Churchill Mk.VII
Heavy Tank - Great Britain (GB)
| Category | Name |
|-|-|
| **Main Cannon** | `OQF 57MM [Churchill Mk.VII]` |
| **Coaxial Machine Gun** | `COAXIAL BESA 7.92mm [Churchill Mk.VII]` |
| **Hull Machine Gun** | `HULL BESA 7.92mm [Churchill Mk.VII]` |

### Commander Abilities
Names are the same across factions.
| Category | Name |
|-|-|
| **Bombing Run** | `BOMBING RUN` |
| **Strafing Run** | `STRAFING RUN` |
| **Precision Strike** | `PRECISION STRIKE` |
| **Katyusha Barrage** | `Unknown` |
<sup>* Kills with Katyusha Barrage show as "Unknown".

### Removed Weapons
| Name | Comment |
|-|-|
| `Lee-Enfield Pattern 1914` | Removed in U14.5 for SMLE No.1 Mk III |

### Bugged Weapon Names
| Name | Comment |
|-|-|
| `FireSpot` | Rarely seen when a RUS Assault player kills with a Molotov. Cause of "FireSpot" instead of "MOLOTOV" is unknown, needs testing. |
| `UNKNOWN` | Seen when the killer’s reference is lost, e.g., a bleeding player gives up after their attacker dies or disconnects.

## Loadouts
Loadouts define the equipment assigned to players based on their faction and role. Loadout items (e.g., weapons, grenades) correspond to the items listed in the [Available Weapons](#available-weapons) section. Loadout names can be retrieved via the `GetServerInformation: player` or `GetServerInformation: players` commands, which return the `loadout` field as a string (e.g., `"NCO"`, `"Standard Issue"`).

**Available Loadout Names**:
- **United States (US)**:
  - **Commander**: Standard Issue, Veteran
  - **Officer**: Standard Issue, Point Man, NCO
  - **Rifleman**: Standard Issue, Point Man
  - **Assault**: Standard Issue, Veteran, Grenadier, Raider
  - **Automatic Rifleman**: Standard Issue, Veteran
  - **Medic**: Standard Issue, Corpsman
  - **Support**: Standard Issue, Ammo Carrier, Flamer
  - **Machine Gunner**: Standard Issue, Fire Support
  - **Anti-Tank**: Standard Issue, Gun Crew
- **British 8th Army (B8A)**:
  - **Commander**: Standard Issue, Veteran
  - **Officer**: Standard Issue, Point Man, NCO
  - **Rifleman**: Standard Issue, Point Man
  - **Assault**: Standard Issue, Veteran, Grenadier, Raider
  - **Automatic Rifleman**: Standard Issue, Drum Gunner
  - **Medic**: Standard Issue, Corpsman
  - **Support**: Standard Issue, Ammo Carrier, Flamer
  - **Machine Gunner**: Standard Issue, Veteran
  - **Anti-Tank**: Standard Issue, Gun Crew, Ambusher, Elephant Gunner
  - **Engineer**: Standard Issue, Sapper, Field Engineer
  - **Tank Commander**: Standard Issue, Mechanic
  - **Crewman**: Standard Issue, Mechanic
  - **Spotter**: Standard Issue, Scout
  - **Sniper**: Standard Issue, Veteran
- **Germany (GER), Soviet Union (SOV), Deutsches Afrikakorps (DAK)**:
  - Loadouts for these factions are not defined in the provided data but may be available in additional configuration files or via the game’s internal data. Use `GetServerInformation: player` or `GetServerInformation: players` to retrieve loadout names for these factions.

**Note**: Loadout items are specific to each faction and role, and their names (e.g., `M1A1 THOMPSON`, `Mills Bomb`) align with the weapons listed in the [Available Weapons](#available-weapons) section.

## JSON Schemas (Selected Responses)
> Shapes shown here are abbreviated for readability.

**Player**
```json
{
  "name":"string","clanTag":"string|null","iD":"string","platform":"steam|epic|xbl|psn|ps5|xsx","eosId":"string",
  "level":0,"team":0-6,"role":0-13,"platoon":"string|null","loadout":"string",
  "kills":0,"deaths":0,
  "scoreData":{"cOMBAT":0,"offense":0,"defense":0,"support":0},
  "worldPosition":{"x":-100000..100000,"y":-100000..100000,"z":float}
}
```

**Map Rotation Entry**
```json
{ "name":"string","gameMode":"id","timeOfDay":"Day|Night|...","iD":"LayerId","position":1 }
```

**Bans Entry**
```json
{ "userId":"string","userName":"string","timeOfBanning":"string","durationHours":int,"banReason":"string","adminName":"string" }
```

**Server Config**
```json
{ "serverName":"string","buildNumber":"string","buildRevision":"string","supportedPlatforms":["Steam","WinGDK","eos"],"passwordProtected":bool }
```

## Notes & Gotchas
- **Versioning**: All commands here use `"version": 2`.
- **Countdown on map change**: `ChangeMap` starts a ~60s countdown; it does not hard-swap immediately.
- **Sector layout**: Use `GetClientReferenceData("SetSectorLayout")` to retrieve valid sector names before calling `SetSectorLayout`.
- **Boolean-ish outcomes**: Some client libraries cast certain HTTP-like status codes to `False` instead of raising:
  - `PunishPlayer` / `ForceTeamSwitch`: status `500` → treated as `False` (e.g., already dead/not present/cannot switch).
  - `KickPlayer`, `RemoveTemporaryBan`, `RemovePermanentBan`: status `400` → treated as `False` (e.g., not found / not banned).
- **Auto-balance threshold**: Setting `AutoBalanceThreshold` to `0` does **not** disable auto-balance; use `SetAutoBalanceEnabled` instead.
- **Dynamic weather**: Only maps that support it will respond; others may no-op.