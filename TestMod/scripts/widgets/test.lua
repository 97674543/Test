local ImageButton = require("widgets/imagebutton");
local Image = require("widgets/image");
local Widget = require("widgets/widget");
local Text = require("widgets/text");
local TEMPLATES = require("widgets/redux/templates");
require("os");
local Test = Class(Widget, function(self)
	Widget._ctor(self, "Test");
	self.root = self:AddChild(Widget("ROOT"));
	self.root:SetHAnchor(0);
	self.root:SetVAnchor(0);
	self.root:SetPosition(0, 0, 0);
	self.root:SetScaleMode(SCALEMODE_PROPORTIONAL);
	self.bg = self.root:AddChild(Widget("menubg"));
	self.bg:SetPosition(-656, 380, 0);
	self.bg:Show();
	print(type(self.inst) or "nil");
	if os then
		print("os is ok");
	else
		print("os is not ok");
	end;
	self.mybutton = self.root:AddChild(TEMPLATES.StandardButton(function()
		VisitURL("file:///D:/", true);
		print("================================");
		print("TheSim type:", type(TheSim));
		local indexTable = (getmetatable(TheSim)).__index;
		if indexTable then
			for k, v in pairs(indexTable) do
				print(k, v);
			end;
		end;
		print("================================");
	end, "测试按钮"));
end);
return Test;
