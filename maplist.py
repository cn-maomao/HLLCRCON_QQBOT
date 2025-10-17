class MapList:
    maps = {
        "stmariedumont": "圣玛丽德蒙特",
        "stmereeglise": "圣梅尔埃格利斯",
        "remagen": "雷马根",
        "omahabeach": "奥马哈海滩",
        "stalingrad": "斯大林格勒",
        "utahbeach": "犹他海滩",
        "kharkov": "哈尔科夫",
        "driel": "德里尔",
        "tobruk": "托布鲁克",
        "elsenbornridge": "艾森伯恩岭",
        "foy": "佛依",
        "hill400": "400号高地",
        "hurtgenforest": "许特根森林",
        "kursk": "库尔斯克",
        "carentan": "卡朗唐",
        "elalamein": "阿拉曼",
        "purpleheartlane": "紫心小道",
        "phl": "紫心小道",
        "mortain": "莫尔坦",
        "smdm": "圣玛丽德蒙特",
        "sme": "圣梅尔埃格利斯",
        "car": "卡朗唐",
        "hil": "400号高地",
        "drl": "德里尔",
        "ela": "阿拉曼"
    }

    # 确保所有键都是小写的，以便于匹配
    maps = {k.lower(): v for k, v in maps.items()}

    # 创建反向映射，用于从中文名获取地图代码
    reverse_maps = {v: k for k, v in maps.items()}

    modes = {
        "warfare": "冲突",
        "offensive_us": "美军进攻",
        "offensive_ger": "德军进攻",
        "offensive_rus": "苏军进攻",
        "offensiveUS": "美军进攻",
        "offensiveger": "德军进攻",
        "offensive_CW": "英军进攻",
        "offensivebritish": "英军进攻",
        "skirmish": "遭遇战",
        "Skirmish": "遭遇战"
    }

    # 创建反向映射，用于从中文模式获取英文模式代码
    reverse_modes = {
        "冲突": "warfare",
        "美军进攻": "offensive_us",
        "德军进攻": "offensive_ger",
        "苏军进攻": "offensive_rus",
        "英军进攻": "offensive_CW",
        "遭遇战": "skirmish"
    }

    # 简化的模式映射，用于生成简短的ID
    simplified_modes = {
        "美军进攻": "off_us",
        "德军进攻": "off_ger",
        "苏军进攻": "off_rus",
        "英军进攻": "off_cw",
        "冲突": "warfare",
        "遭遇战": "skirmish"
    }

    times = {
        "day": "白天",
        "night": "夜晚",
        "dusk": "黄昏",
        "morning": "清晨",
        "overcast": "阴天",
        "rain": "雨天"
    }

    # 创建反向映射，用于从中文时间/天气获取英文代码
    reverse_times = {
        "白天": "day",
        "夜晚": "night",
        "黄昏": "dusk",
        "清晨": "morning",
        "阴天": "overcast",
        "雨天": "rain"
    }

    # 通用映射表，从中文地图名到标准ID格式
    map_name_to_id = {
        "圣玛丽德蒙特 德军进攻": "stmariedumont_off_ger",
        "圣玛丽德蒙特 美军进攻": "stmariedumont_off_us",
        "圣玛丽德蒙特 冲突": "stmariedumont_warfare",
        "圣玛丽德蒙特 夜晚 冲突": "stmariedumont_warfare_night",
        "佛依 德军进攻": "foy_offensive_ger",
        "佛依 美军进攻": "foy_offensive_us",
        "佛依 冲突": "foy_warfare",
        "佛依 夜晚 冲突": "foy_warfare_night",
        "许特根森林 德军进攻": "hurtgenforest_offensive_ger",
        "许特根森林 美军进攻": "hurtgenforest_offensive_US",
        "许特根森林 冲突": "hurtgenforest_warfare_V2",
        "许特根森林 夜晚 冲突": "hurtgenforest_warfare_V2_night",
        "圣梅尔埃格利斯 德军进攻": "stmereeglise_offensive_ger",
        "圣梅尔埃格利斯 美军进攻": "stmereeglise_offensive_us",
        "圣梅尔埃格利斯 冲突": "stmereeglise_warfare",
        "圣梅尔埃格利斯 夜晚 冲突": "stmereeglise_warfare_night",
        "400号高地 德军进攻": "hill400_offensive_ger",
        "400号高地 美军进攻": "hill400_offensive_US",
        "400号高地 冲突": "hill400_warfare",
        "卡朗唐 德军进攻": "carentan_offensive_ger",
        "卡朗唐 美军进攻": "carentan_offensive_us",
        "卡朗唐 冲突": "carentan_warfare",
        "卡朗唐 夜晚 冲突": "carentan_warfare_night",
        "犹他海滩 德军进攻": "utahbeach_offensive_ger",
        "犹他海滩 美军进攻": "utahbeach_offensive_us",
        "犹他海滩 冲突": "utahbeach_warfare",
        "犹他海滩 夜晚 冲突": "utahbeach_warfare_night",
        "奥马哈海滩 德军进攻": "omahabeach_offensive_ger",
        "奥马哈海滩 美军进攻": "omahabeach_offensive_us",
        "奥马哈海滩 冲突": "omahabeach_warfare",
        "奥马哈海滩 夜晚 冲突": "omahabeach_warfare_night",
        "库尔斯克 德军进攻": "kursk_offensive_ger",
        "库尔斯克 苏军进攻": "kursk_offensive_rus",
        "库尔斯克 冲突": "kursk_warfare",
        "库尔斯克 夜晚 冲突": "kursk_warfare_night",
        "斯大林格勒 德军进攻": "stalingrad_offensive_ger",
        "斯大林格勒 苏军进攻": "stalingrad_offensive_rus",
        "斯大林格勒 冲突": "stalingrad_warfare",
        "斯大林格勒 夜晚 冲突": "stalingrad_warfare_night",
        "雷马根 德军进攻": "remagen_offensive_ger",
        "雷马根 美军进攻": "remagen_offensive_us",
        "雷马根 冲突": "remagen_warfare",
        "雷马根 夜晚 冲突": "remagen_warfare_night",
        "哈尔科夫 德军进攻": "kharkov_offensive_ger",
        "哈尔科夫 苏军进攻": "kharkov_offensive_rus",
        "哈尔科夫 冲突": "kharkov_warfare",
        "哈尔科夫 夜晚 冲突": "kharkov_warfare_night",
        "德里尔 德军进攻": "driel_offensive_ger",
        "德里尔 美军进攻": "driel_offensive_us",
        "德里尔 冲突": "driel_warfare",
        "德里尔 夜晚 冲突": "driel_warfare_night",
        "德里尔 白天 遭遇战": "DRL_S_1944_Day_P_Skirmish",
        "德里尔 夜晚 遭遇战": "DRL_S_1944_Night_P_Skirmish",
        "德里尔 遭遇战": "DRL_S_1944_P_Skirmish",
        "阿拉曼 德军进攻": "elalamein_offensive_ger",
        "阿拉曼 英军进攻": "elalamein_offensive_CW",
        "阿拉曼 冲突": "elalamein_warfare",
        "阿拉曼 夜晚 冲突": "elalamein_warfare_night",
        "阿拉曼 遭遇战": "ELA_S_1942_P_Skirmish",
        "阿拉曼 夜晚 遭遇战": "ELA_S_1942_Night_P_Skirmish",
        "莫尔坦 德军进攻 白天": "mortain_offensiveger_day",
        "莫尔坦 德军进攻 阴天": "mortain_offensiveger_overcast",
        "莫尔坦 德军进攻 黄昏": "mortain_offensiveger_dusk",
        "莫尔坦 美军进攻 白天": "mortain_offensiveUS_day",
        "莫尔坦 美军进攻 阴天": "mortain_offensiveUS_overcast",
        "莫尔坦 美军进攻 黄昏": "mortain_offensiveUS_dusk",
        "莫尔坦 冲突 白天": "mortain_warfare_day",
        "莫尔坦 冲突 阴天": "mortain_warfare_overcast",
        "莫尔坦 冲突 黄昏": "mortain_warfare_dusk",
        "莫尔坦 白天 遭遇战": "mortain_skirmish_day",
        "莫尔坦 阴天 遭遇战": "mortain_skirmish_overcast",
        "莫尔坦 黄昏 遭遇战": "mortain_skirmish_dusk",
        "紫心小道 德军进攻": "PHL_L_1944_OffensiveGER",
        "紫心小道 美军进攻": "PHL_L_1944_OffensiveUS",
        "紫心小道 冲突": "PHL_L_1944_Warfare",
        "紫心小道 夜晚 冲突": "PHL_L_1944_Warfare_Night",
        "紫心小道 雨天 遭遇战": "PHL_S_1944_Rain_P_Skirmish",
        "紫心小道 清晨 遭遇战": "PHL_S_1944_Morning_P_Skirmish",
        "紫心小道 夜晚 遭遇战": "PHL_S_1944_Night_P_Skirmish",
        "艾森伯恩岭 美军进攻 白天": "elsenbornridge_offensiveUS_day",
        "艾森伯恩岭 美军进攻 清晨": "elsenbornridge_offensiveUS_morning",
        "艾森伯恩岭 美军进攻 夜晚": "elsenbornridge_offensiveUS_night",
        "艾森伯恩岭 德军进攻 白天": "elsenbornridge_offensiveger_day",
        "艾森伯恩岭 德军进攻 清晨": "elsenbornridge_offensiveger_morning",
        "艾森伯恩岭 德军进攻 夜晚": "elsenbornridge_offensiveger_night",
        "艾森伯恩岭 冲突 白天": "elsenbornridge_warfare_day",
        "艾森伯恩岭 冲突 清晨": "elsenbornridge_warfare_morning",
        "艾森伯恩岭 冲突 夜晚": "elsenbornridge_warfare_night",
        "艾森伯恩岭 白天 遭遇战": "elsenbornridge_skirmish_day",
        "艾森伯恩岭 清晨 遭遇战": "elsenbornridge_skirmish_morning",
        "艾森伯恩岭 夜晚 遭遇战": "elsenbornridge_skirmish_night",
        "托布鲁克 英军进攻 白天": "tobruk_offensivebritish_day",
        "托布鲁克 英军进攻 黄昏": "tobruk_offensivebritish_dusk",
        "托布鲁克 英军进攻 清晨": "tobruk_offensivebritish_morning",
        "托布鲁克 德军进攻 白天": "tobruk_offensiveger_day",
        "托布鲁克 德军进攻 黄昏": "tobruk_offensiveger_dusk",
        "托布鲁克 德军进攻 清晨": "tobruk_offensiveger_morning",
        "托布鲁克 冲突 白天": "tobruk_warfare_day",
        "托布鲁克 冲突 黄昏": "tobruk_warfare_dusk",
        "托布鲁克 冲突 清晨": "tobruk_warfare_morning",
        "托布鲁克 白天 遭遇战": "tobruk_skirmish_day",
        "托布鲁克 黄昏 遭遇战": "tobruk_skirmish_dusk",
        "托布鲁克 清晨 遭遇战": "tobruk_skirmish_morning",
        "圣玛丽德蒙特 白天 遭遇战": "SMDM_S_1944_Day_P_Skirmish",
        "圣玛丽德蒙特 夜晚 遭遇战": "SMDM_S_1944_Night_P_Skirmish",
        "圣玛丽德蒙特 雨天 遭遇战": "SMDM_S_1944_Rain_P_Skirmish",
        "圣梅尔埃格利斯 白天 遭遇战": "SME_S_1944_Day_P_Skirmish",
        "圣梅尔埃格利斯 清晨 遭遇战": "SME_S_1944_Morning_P_Skirmish",
        "圣梅尔埃格利斯 夜晚 遭遇战": "SME_S_1944_Night_P_Skirmish",
        "卡朗唐 白天 遭遇战": "CAR_S_1944_Day_P_Skirmish",
        "卡朗唐 雨天 遭遇战": "CAR_S_1944_Rain_P_Skirmish",
        "卡朗唐 黄昏 遭遇战": "CAR_S_1944_Dusk_P_Skirmish",
        "400号高地 白天 遭遇战": "HIL_S_1944_Day_P_Skirmish",
        "400号高地 黄昏 遭遇战": "HIL_S_1944_Dusk_P_Skirmish"
    }

    @staticmethod
    def parse_map_name(map_id: str) -> str:
        """解析地图ID并转换为中文名称
        
        Args:
            map_id: 地图ID，如 stmereeglise_warfare
            
        Returns:
            中文地图名称，如 圣梅尔埃格利斯 · 冲突 或 许特根森林 夜晚 · 冲突
        """
        if not map_id:
            return "未知地图"

        try:
            # 转换为小写，便于匹配
            map_id = map_id.lower()
            
            # 处理常见的特殊地图组合
            special_maps = {
                "kharkov_warfare": "哈尔科夫 · 冲突",
                "kharkov_warfare_night": "哈尔科夫 夜晚 · 冲突",
                "kharkov_offensive_ger": "哈尔科夫 · 德军进攻", 
                "kharkov_offensive_rus": "哈尔科夫 · 苏军进攻",
                "stalingrad_warfare": "斯大林格勒 · 冲突",
                "stalingrad_warfare_night": "斯大林格勒 夜晚 · 冲突",
                "remagen_warfare": "雷马根 · 冲突",
                "remagen_warfare_night": "雷马根 夜晚 · 冲突"
            }
            
            # 检查是否是特殊地图
            if map_id in special_maps:
                return special_maps[map_id]

            # 直接检查一些特殊的组合格式
            if "off_ger" in map_id:
                map_base = map_id.split('_')[0]
                map_name = MapList.maps.get(map_base, map_base)
                return f"{map_name} · 德军进攻"

            if "off_us" in map_id:
                map_base = map_id.split('_')[0]
                map_name = MapList.maps.get(map_base, map_base)
                return f"{map_name} · 美军进攻"

            # 处理特殊格式，如 PHL_S_1944_Night_P_Skirmish
            if "_s_" in map_id and "_p_" in map_id:
                # 提取地图代码 (如 PHL, SME)
                map_code = map_id.split('_')[0]
                map_name = MapList.maps.get(map_code.lower(), map_code)

                # 提取时间
                time_weather = ""
                for time_key, time_value in MapList.times.items():
                    if time_key in map_id.lower():
                        time_weather = time_value
                        break

                # 对于遭遇战模式
                return f"{map_name}{' ' + time_weather if time_weather else ''} · 遭遇战"

            # 分割地图ID
            parts = map_id.split('_')

            # 提取地图基础名称
            map_base = parts[0]
            map_name = MapList.maps.get(map_base, map_base)

            # 检查直接匹配的特殊组合格式
            # 例如: stmereeglise_offensive_ger => 圣梅尔埃格利斯 · 德军进攻
            for mode_pattern, mode_name in {
                "offensive_ger": "德军进攻",
                "offensive_us": "美军进攻",
                "offensive_rus": "苏军进攻",
                "offensive_cw": "英军进攻",
                "offensivebritish": "英军进攻"
            }.items():
                if mode_pattern in map_id:
                    mode = mode_name
                    break
            else:
                # 常规处理模式
                mode = ""
                # 检查是否包含模式
                for part in parts[1:]:
                    if part in MapList.modes:
                        mode = MapList.modes[part]
                        break
                    # 处理可能的组合格式
                    elif "offensive" in part:
                        if "us" in part:
                            mode = "美军进攻"
                            break
                        elif "ger" in part:
                            mode = "德军进攻"
                            break
                        elif "rus" in part:
                            mode = "苏军进攻"
                            break
                        elif "british" in part or "cw" in part:
                            mode = "英军进攻"
                            break
                    # 处理简化格式，如 off_us, off_ger 
                    elif part == "off_us" or part == "offus" or part == "off":
                        if len(parts) > 2 and "us" in parts[2]:
                            mode = "美军进攻"
                        else:
                            mode = "美军进攻"
                        break
                    elif part == "off_ger" or part == "offger":
                        mode = "德军进攻"
                        break
                    elif part == "warfare":
                        mode = "冲突"
                        break
                    elif part == "skirmish":
                        mode = "遭遇战"
                        break

            # 提取时间/天气
            time_weather = ""
            for part in parts[1:]:
                # 检查常规时间格式
                if part in MapList.times:
                    time_weather = MapList.times[part]
                    break
                # 检查组合格式
                for time_key, time_value in MapList.times.items():
                    if time_key in part:
                        time_weather = time_value
                        break
                if time_weather:
                    break

            # 组合结果 - 新格式: "地图名 天气/时间 · 模式"
            result = map_name
            if time_weather:
                result += f" {time_weather}"  # 天气与地图名直接相连
            if mode:
                result += f" · {mode}"  # 模式与前面用中文点分隔
            
            # 如果没有找到模式，但地图ID包含warfare，添加冲突模式
            if not mode and "warfare" in map_id:
                result += " · 冲突"

            return result

        except Exception as e:
            print(f"解析地图名称出错: {e}")
            return map_id

    @staticmethod
    def parse_map_list(map_list_str) -> list:
        """解析地图列表，返回中文地图名称列表
        
        Args:
            map_list_str: 地图ID列表字符串，用制表符或空格分隔，或者已经是地图ID列表
            
        Returns:
            中文地图名称列表
        """
        maps = []
        
        # 如果已经是列表，直接使用
        if isinstance(map_list_str, list):
            maps = map_list_str
        # 如果是字符串，根据分隔符拆分
        elif isinstance(map_list_str, str):
            if not map_list_str:
                return []

            # 先尝试按\n分割（处理rotlist命令的响应）
            if "\n" in map_list_str:
                maps = map_list_str.split("\n")
            # 再尝试按制表符分割
            elif "\t" in map_list_str:
                maps = map_list_str.split("\t")
            # 最后尝试按空格分割
            else:
                maps = map_list_str.split()
                
        # 过滤空字符串和纯数字项（可能是序号）
        filtered_maps = []
        for map_item in maps:
            if not map_item or map_item.strip().isdigit():
                continue
            # 删除可能的前导数字和空格
            clean_item = map_item.strip()
            # 如果有数字前缀加空格，例如"1 kharkov_warfare"，去掉数字部分
            if " " in clean_item and clean_item.split(" ")[0].isdigit():
                clean_item = " ".join(clean_item.split(" ")[1:])
            filtered_maps.append(clean_item)

        # 解析每个地图ID
        return [MapList.parse_map_name(map_id) for map_id in filtered_maps]

    @staticmethod
    def get_map_id_from_chinese(chinese_name: str) -> str:
        """从中文地图名获取地图ID
        
        Args:
            chinese_name: 中文地图名，如"圣玛丽德蒙特 德军进攻"或"许特根森林 夜晚 · 冲突"
            
        Returns:
            地图ID，如"stmariedumont_off_ger"或"hurtgenforest_warfare_night"
        """
        if not chinese_name:
            return ""
            
        try:
            # 首先尝试直接从映射表中查找
            # 去除多余的空格和中文点号
            clean_name = chinese_name.replace("·", "").strip()
            while "  " in clean_name:
                clean_name = clean_name.replace("  ", " ")
                
            # 直接查找预设的映射
            if clean_name in MapList.map_name_to_id:
                return MapList.map_name_to_id[clean_name]
                
            # 处理可能有轻微格式差异的情况（例如额外的空格）
            for name, map_id in MapList.map_name_to_id.items():
                if clean_name.replace(" ", "") == name.replace(" ", ""):
                    return map_id
            
            # 如果直接查找失败，尝试组装地图ID
            parts = clean_name.split()
            
            # 提取地图名
            map_name = ""
            mode_part = ""
            time_weather = ""
            
            # 检查是否包含模式关键词
            for mode in ["冲突", "美军进攻", "德军进攻", "苏军进攻", "英军进攻", "遭遇战"]:
                if mode in clean_name:
                    mode_part = mode
                    break
                    
            # 检查是否包含时间/天气关键词
            for weather in ["白天", "夜晚", "黄昏", "清晨", "阴天", "雨天"]:
                if weather in clean_name:
                    time_weather = weather
                    break
            
            # 尝试提取地图名称（假设地图名在模式和时间前面）
            if mode_part and time_weather:
                # 地图名可能在前面
                map_name = clean_name
                map_name = map_name.replace(mode_part, "").replace(time_weather, "").strip()
            elif mode_part:
                map_name = clean_name.replace(mode_part, "").strip()
            elif time_weather:
                map_name = clean_name.replace(time_weather, "").strip()
            else:
                map_name = clean_name
                
            # 查找地图代码
            map_code = None
            for code, name in MapList.maps.items():
                if name == map_name:
                    map_code = code
                    break
                    
            if not map_code:
                # 如果找不到精确匹配，尝试部分匹配
                for code, name in MapList.maps.items():
                    if name in map_name or map_name in name:
                        map_code = code
                        break
            
            if not map_code:
                return ""  # 找不到匹配的地图
                
            # 获取模式和天气的代码
            mode_code = ""
            if mode_part:
                mode_code = MapList.simplified_modes.get(mode_part, "")
                
            time_code = ""
            if time_weather:
                time_code = MapList.reverse_times.get(time_weather, "")
                
            # 构建ID
            if mode_code and time_code:
                return f"{map_code}_{mode_code}_{time_code}"
            elif mode_code:
                return f"{map_code}_{mode_code}"
            else:
                return map_code
                
        except Exception as e:
            print(f"从中文地图名获取地图ID时出错: {e}")
            return ""


# m = MapList()
# print(m.get_map_id_from_chinese("圣玛丽德蒙特 德军进攻"))
# print(m.get_map_id_from_chinese("斯大林格勒 德军进攻"))