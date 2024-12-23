--[[
        作品:清理注释
        作者:馒头
        下面是我去掉注释以后的内容(可能不太准确,仅供参考!)
--]] 

local function CopyString(inputStr, repeatCount) 
    local resultStr = ""
    local repeatCount = type(repeatCount) == "number" and repeatCount or 1
    if type(inputStr) ~= "string" then return "" end 
    for i = 1, repeatCount do
        resultStr = resultStr .. inputStr 
    end
    return resultStr
end 
local function formatChar(...)
    local s = ""
    local t = {...}
    for _,v in ipairs(t) do 
        s = s .. string.format("\\%s",v)
    end
    return string.format("\"%s\"",s)
end
local function NoContainsStr(str,...) 
    if type(str) ~= "string" then print("NoContainsStr:参数1不是字符串 or null") return end 
    local tab = {...} or {}
    for k,v in pairs(tab) do 
        if v and type(v) == "string" then 
            if string.match(str,v) then return false end
        end
    end 
    return true 
end 
local function Punctuations(s) 
    local S = s and tostring(s) 
    local punctuations = {}
    for word in string.gmatch("^$().[]*+-?","[%p]") do 
        punctuations[#punctuations+1] = word
    end
    S = string.gsub(S,"%%","%%%%")
    for k,v in ipairs(punctuations) do 
        local a = string.format("%q","%"..v)
        if string.match(S,"%"..v) then 
            S = string.gsub(S,"%"..v,"%%"..v)
        end
    end
    return S 
end
local function ClearMultiLineComments(filePath, createCopy) 
    local filePath = filePath and tostring(filePath) .. ".lua" 
    if not filePath then return end 
    filePath = createCopy and filePath .. " - copy.lua" or filePath .. ".lua" 
    local file = io.open(filePath) 
    if file then 
        local script = file:read('*a') 
        file:close() 
        local str = string.match(script, "[^-]-%-%-%[%[.-%]%]") 
        if str then 
            local file = io.open(filePath, 'w') 
            local script = (string.gsub(script, "[^%-]-%-%-%[%[.-%]%]", "")) 
            if file then 
                file:write(script) 
                file:close() 
            end 
            print("ClearMultiLineComments:多行注释已删除", filePath) 
        else 
            print("ClearMultiLineComments:没找到多行注释") 
        end 
    else 
        print("ClearMultiLineComments:多行注释没找到", filePath, "这个文件") 
    end 
end 
local function ClearMultiLineComments(filePath, createCopy) 
    local filePath = filePath and tostring(filePath) .. ".lua" 
    if not filePath then return end 
    filePath = createCopy and filePath .. " - copy.lua" or filePath .. ".lua" 
    local loop = 0 
    repeat 
        local file = io.open(filePath) 
        if file then 
            local script = file:read('*a') 
            file:close() 
            local data = "%-%-%[("..CopyString("%=",loop)..")%[.-%](%=*)%]" 
            local str = string.match(script, data) 
            if str then 
                local file = io.open(filePath, 'w') 
                local script = (string.gsub(script, data, "")) 
                if file then 
                    file:write(script) 
                    file:close() 
                end 
                print(string.format("ClearMultiLineComments:删除多行注释 [...] === (%u)",loop))
            else 
            end 
        else 
            print(string.format("ClearMultiLineComments:多行注释没找到 '%s' 这个文件",filePath)) 
            return
        end 
        loop = loop + 1 
    until loop > 15
    print("ClearMultiLineComments:多行注释已删除",loop, filePath) 
end 
local function ClearSingleLineComments(filePath) 
    local filePath = filePath and tostring(filePath) .. ".lua" 
    if not filePath then return end 
    local file = io.open(filePath) 
    if file then 
        local data = "%-%-.*" 
        local data1 = "%-%-%[%=-%[" 
        local data2 = "%-%-%]%=-%]" 
        local newfile = io.open(filePath .. " - copy.lua", "w") 
        local tab = {}
        for line in file:lines() do 
            local script = NoContainsStr(line,data1,data2) and (string.gsub(line, "(%-%-.+)", " ")) or line.." " 
            if newfile then newfile:write(script.."\n") end 
            tab[#tab+1] = line
            -- print(line)
        end 
        print(#tab)
        file:close() 
        newfile:close()
        print("ClearSingleLineComments:单行注释已删除 - 并创建了一个副本文件", 
              filePath .. " - copy.lua", filePath) 
    else
        print(string.format("ClearSingleLineComments:单行注释没找到 '%s' 这个文件",filePath)) 
        return 
    end 
    return true
end 
local function ClearSingleLineCommentsAgain(filePath, createCopy) 
    local filePath = filePath and tostring(filePath) 
    if not filePath then return end 
    filePath = createCopy and filePath .. ".lua - copy.lua" or filePath .. ".lua" 
    local file1 = io.open(filePath) 
    if file1 then 
        local data = "%-%-.*" 
        local file = io.open("Staging.lua", "w") 
        local file2 = io.open(filePath) 
        for line in file2:lines() do 
            local script = (string.gsub(line, "(%-%-.+)", "")) 
            if file then file:write(script.."\n") end 
        end 
        file2:close() 
        file:close() 
        print("ClearSingleLineCommentsAgain:残余单行注释已删除 - 并创建了一个临时文件Staging.lua", filePath) 
    else
        print(string.format("ClearSingleLineCommentsAgain:残余单行注没找到 '%s' 这个文件",filePath)) 
        return
    end 
    return true
end 
local function RemoveExtraSpaces(filePath, createCopy) 
    local filePath = filePath and tostring(filePath) 
    if not filePath then return end 
    filePath = createCopy and filePath .. ".lua" or filePath .. ".lua - copy.lua" 
    local file = io.open(filePath) 
    if file then 
        local script = file:read('*a') 
        file:close() 
        local str = string.match(script, "(%s+)\n") 
        if str then 
            local file = io.open(filePath, 'w') 
            local script = (string.gsub(script, "(%s+)\n", " \n")) 
            if file then 
                file:write(script) 
                file:close() 
            end 
        end 
        print("RemoveExtraSpaces:多余空格已删除",filePath) 
    else 
        print(string.format("RemoveExtraSpaces:清理多余空格没找到 '%s' 这个文件",filePath)) 
        return false
    end 
    return true
end 
local function RemoveExtraSpacesAgain(filePath, createCopy) 
    local filePath = filePath and tostring(filePath) 
    if not filePath then return end 
    filePath = createCopy and filePath .. ".lua" or filePath .. ".lua - copy.lua" 
    local file = io.open(filePath) 
    if file then 
        local script = file:read('*a') 
        file:close() 
        local str = string.match(script, "(%s+)") 
        if str then 
            local file = io.open(filePath, 'w') 
            local script = (string.gsub(script, "(%s+)", " ")) 
            if file then 
                file:write(script) 
                file:close() 
            end 
        end 
        print("RemoveExtraSpacesAgain:转成一行已完成", filePath) 
    else 
        print(string.format("RemoveExtraSpacesAgain:转成一行没找到 '%s' 这个文件",filePath)) 
        return false
    end 
    return true
end 
local function ConnectString(filePath, createCopy) 
    local filePath = type(filePath) == "string" and tostring(filePath) 
    if not filePath then return end 
    filePath = createCopy and filePath .. ".lua" or filePath .. ".lua - copy.lua" 
    local loop = 0 
    local tab = {}
    repeat
        local file = io.open(filePath) 
        loop = loop + 1 
        if file then 
            local script = file:read('*a') 
            file:close() 
            local data = "%\"%s-%.%.%s-%\"" 
            local data1 = "%\"%s-%.%.%s-%(%s-\"%s-.[^%)%\"]-%s-\"%s-%)" 
            local data2 = "%(%s-\"%s-.[^%(%\"]-%s-\"%s-%)%s-%.%.%s-%\"" 
            local data3 = "%\"%s-%)%s-%.%.%s-%(%s-%\"" 
            local str = string.match(script, data) 
            local str1 = "" 
            if not str then 
                str = string.match(script, data1) 
                str1 = str and string.gsub(str,"[%\"%s-%.%s%(%)]","").."\"" 
            end 
            if not str then 
                str = string.match(script, data2) 
                str1 = str and "\"" .. string.gsub(str,"[%\"%s-%.%s%(%)]","")
            end 
            if not str then 
                str = string.match(script, data3) 
                str1 = str and ""
            end 
            print(str)
            print(str1)
            str = str and (string.gsub(str,"%.","%%."))
            str = str and (string.gsub(str,"%(","%%("))
            str = str and (string.gsub(str,"%)","%%)")) 
            str = str and (string.gsub(str,"%:","%%:")) 
            str = str and (string.gsub(str,"%_","%%_")) 
            str = str and (string.gsub(str,"%[","%%[")) 
            str = str and (string.gsub(str,"%]","%%]")) 
            str = str and (string.gsub(str,"%\"","%%\"")) 
            str = str and (string.gsub(str,"%\'","%%\'")) 
            str = str and (string.gsub(str,"%/","%%/")) 
            if str then 
                local file = io.open(filePath, 'w') 
                local script = (string.gsub(script, str, str1)) 
                if file then 
                    file:write(script) 
                    file:close() 
                end 
                print(string.format("ConnectString:连接字符串 === (%u)",loop)) 
            else 
                print("ConnectString:连接字符串 已完成", filePath) 
                return 
            end 
        else 
            print(string.format("ConnectString:连接字符串 没找到 '%s' 这个文件",filePath)) 
            return false
        end 
    until loop <= 0 
    return true
end 
local function RemoveCharacter(filePath, createCopy) 
    local filePath = type(filePath) == "string" and tostring(filePath) 
    if not filePath then return end 
    local data = "(string.char%(.-%))"
    local data = "(string.char[%(%\'%\"].-[%\'%\"%)])" 
    local data = "(string.char[%(%\'%\"].-[%\'%\"%)])" 
    filePath = createCopy and filePath .. ".lua" or filePath .. ".lua - copy.lua" 
    local loop = 0 
    repeat
        local file = io.open(filePath) 
        loop = loop + 1 
        if file then 
            local script = file:read('*a') 
            file:close() 
            local str = string.match(script, data) 
            local str1 = str and load("return "..str)() 
            local str2 = ""
            for i = 1, str1 and #str1 or 0 do 
                str2 = str2 .. "\\" .. string.format("%03d",string.byte(str1,i))
            end
            str2 = string.format("(\"%s\")",str2)
            if str then 
                str = Punctuations(str)     
                print(str)
                print(str2)
                local file = io.open(filePath, 'w') 
                local script = (string.gsub(script, str, str2))
                if file then 
                    file:write(script) 
                    file:close() 
                end 
                print(string.format("RemoveCharacter:去除 string.char() === (%u)",loop)) 
            else
                print("RemoveCharacter: string.char() 已全部去除", filePath)
                return 
            end 
        else 
            print(string.format("RemoveCharacter:没找到 '%s' 这个文件",filePath))
            return
        end
    until loop <= 0
end 
local function RemoveReverseString(filePath, createCopy) 
    local filePath = type(filePath) == "string" and tostring(filePath) 
    if not filePath then return end 
    local data = "(%(%s-%\"%s-[%w_]-%s-%\"%s-%):reverse%(%))" 
    local data = "(%(%s-%\"%s-[^%(%))]-%s-%\"%s-%):reverse%(%))" 
    filePath = createCopy and filePath .. ".lua" or filePath .. ".lua - copy.lua" 
    local loop = 0 
    repeat
        local file = io.open(filePath) 
        loop = loop + 1 
        if file then 
            local script = file:read('*a') 
            file:close() 
            local str = string.match(script, data) 
            local str1 = str and (load("return "..str)()) 
            str1 = str1 and formatChar(string.byte(str1,1,#str1))
            str1 = str1 and string.format("(%s)",str1) 
            str = str and (string.gsub(str,"%.","%%."))
            str = str and (string.gsub(str,"%(","%%("))
            str = str and (string.gsub(str,"%)","%%)")) 
            str = str and (string.gsub(str,"%:","%%:")) 
            str = str and (string.gsub(str,"%_","%%_")) 
            if str then 
                local file = io.open(filePath, 'w') 
                local script = (string.gsub(script, str, str1))
                if file then 
                    file:write(script) 
                    file:close() 
                end 
                print(string.format("RemoveReverseString:去除 string:reverse() === (%u)",loop)) 
            else
                print("RemoveReverseString: string:reverse() 已全部去除", filePath)
                return 
            end 
        else 
            print(string.format("RemoveReverseString:没找到 '%s' 这个文件",filePath))
            return
        end
    until loop <= 0
    return true
end 
local function ConvertToReadableString(filePath, createCopy) 
    local filePath = type(filePath) == "string" and tostring(filePath) 
    if not filePath then return end 
    filePath = createCopy and filePath .. ".lua" or filePath .. ".lua - copy.lua" 
    local data = "%\"%s-%\\+[%\\%d%d%d]+%s-%\"" 
    local data = "%\"%s*%\\[%\\%d%s/_:]+%s*%\"" 
    -- local data = "%[%'[%\\%d]+.%'%]"
    -- local data = "%'[%\\%d]+.%'"
    -- local data = "%'[^']+.%'"
    local loop = 0 
    repeat
        local file = io.open(filePath) 
        loop = loop + 1 
        if file then 
            local script = file:read('*a') 
            file:close() 
            local str = string.match(script, data) 
            -- str = str and string.gsub(str,"[%[%]]","")
            -- print(str or "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            -- break
            local str1 = str and load("return '".. str.."'")() 
            -- local str1 = str and ' "'..load("return ".. str )() ..'" '
            str1 = str1 and string.gsub(str1,"%%","%%%%")
            str1 = str1 and string.gsub(str1,"%-%-","我是杠我是杠")
            str1 = str1 and string.gsub(str1,"\n","\\n")
            str1 = str1 and string.gsub(str1,"%\\%\\%s-","string.char(92,92)")
            if str then 
                local file = io.open(filePath, 'w') 
                local script = (string.gsub(script, str, str1))
                if file then 
                    file:write(script) 
                    file:close() 
                end 
                print(string.format("ConvertToReadableString:字符串转换易阅读模式 [...] === (%u)",loop))
            else 
                print("ConvertToReadableString:字符串转换易阅读模式 已完成", filePath)
                return
            end 
        else
            print(string.format("ConvertToReadableString:没找到 '%s' 这个文件",filePath))
            return false
        end
    until loop <= 0   or  loop > 2500
    return true
end 
local Tools = {}
function Tools:getTimeString(time)
    local hours = math.floor(time / 3600)
    local minutes = math.floor((time % 3600) / 60)
    local seconds = math.floor(time % 60)
    if(hours < 10) then hours = "0"..hours end
    if(minutes < 10) then  minutes = "0"..minutes end
    if(seconds < 10) then seconds = "0"..seconds end 
    local time = (string.format("%d小时%d分钟%d秒:",hours,minutes,seconds)) 
    return time
end 
local function QuickCleanupProcess(filePath, createCopy) 
    local startTime = os.time()
    print("脚本开始运行")
    if ClearSingleLineComments(filePath) == false then return end
    if ClearMultiLineComments(filePath, true) == false then return end
    if ClearSingleLineCommentsAgain(filePath, true) == false then return end
    if RemoveExtraSpaces(filePath) == false then return end
    if RemoveCharacter(filePath) == false then return end
    if RemoveReverseString(filePath) == false then return end
    if ConnectString(filePath) == false then return end
    if ConvertToReadableString(filePath) == false then return end
    print("脚本运行完成\n总耗时: " .. Tools:getTimeString(os.time() - startTime))
end 

-- 互动输入模式
-- print("请输入要清理的文件路径:")
-- local userInputPath = io.read()  -- 获取用户输入的路径
-- QuickCleanupProcess(userInputPath)  -- 调用函数时使用用户输入的路径


-- 获取命令行参数，假设Python传递过来的路径是第一个参数
local filePath = arg[1]
local createCopy = true  -- 这里可以根据实际需求调整是否创建副本等逻辑，示例中先设为true
QuickCleanupProcess(filePath, createCopy)


function zhuanAScii(filename)
local bytes = "'\\"
    local file = io.open(filename..".lua") 
    if file then 
        local script = file:read('*a') 
        file:close() 
        -- print(script)
        for i = 1, #script do
            bytes = bytes .. string.byte(script, i) .. "\\"
        end
        print(load("return ( string.byte('" .. "script" .."'))" )()) 
        print("loadstring("..bytes.."')") 
    end
end


