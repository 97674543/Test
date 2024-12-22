-- 加载 os 库
local require = GLOBAL.require
local test = require("widgets/test")
-- 定义连接功能
local function connect(self)
    self.test = self:AddChild(test())
end

-- 在多玩家主屏幕构造后添加连接功能
AddClassPostConstruct("screens/redux/multiplayermainscreen", connect)
