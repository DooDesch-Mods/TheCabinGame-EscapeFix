local directory = assert(debug.getinfo(1,"S").source:match("^@(.+[/\\])"))
package.path = directory .. "?.lua;" .. package.path
local runtime = require("cabin_runtime")
local mod = runtime.start(directory,require("definition"))
local PAUSE = "/Game/CabinGameContent/HUD/WBP_Pause_Menu.WBP_Pause_Menu_C"
local CLOSE = "BndEvt__WBP_Pause_Menu_Close_B_K2Node_ComponentBoundEvent_0_OnButtonPressedEvent__DelegateSignature"
local NO = "BndEvt__WBP_Pause_Menu_No_B_K2Node_ComponentBoundEvent_12_OnButtonPressedEvent__DelegateSignature"
local SETTINGS_CANCEL = "BndEvt__SettingsMaster_WBP_Cancel_B_K2Node_ComponentBoundEvent_12_OnButtonPressedEvent__DelegateSignature"
local focused = {}
local topFocus = {}
local subviews = {"WBP_BugReport_C","WBP_Credits_C","SettingsMaster_WBP_C"}
local function pauses()
    local result = {}
    for _,widget in ipairs(FindAllOf("WBP_Pause_Menu_C") or {}) do
        if runtime.valid(widget) and widget:IsInViewport() and widget:IsA(PAUSE) then
            local player,world=widget:GetOwningPlayer(),widget:GetWorld()
            if runtime.valid(player) and player:IsLocalController() and runtime.valid(world) and runtime.valid(player:GetWorld())
                and player:GetWorld():GetAddress()==world:GetAddress() then result[#result+1]=widget end
        end
    end
    return result
end
local function sameWorld(a,b) return a:GetWorld():GetAddress()==b:GetWorld():GetAddress() end
local function original(widget,name)
    local callable = widget[name]
    assert(callable,"original menu return function missing: " .. name)
    callable(widget)
end
local function closeTop(pause,context)
    for _,entry in ipairs({
        {class="WBP_BugReport_C",close="BndEvt__WBP_Feedback_ForceClose_B_K2Node_ComponentBoundEvent_12_OnButtonPressedEvent__DelegateSignature"},
        {class="WBP_Credits_C",close="BndEvt__WBP_Credits_Close_B_K2Node_ComponentBoundEvent_0_OnButtonPressedEvent__DelegateSignature"},
    }) do
        for _,widget in ipairs(FindAllOf(entry.class) or {}) do
            if runtime.valid(widget) and widget:IsInViewport() and sameWorld(widget,pause) then
                original(widget,entry.close)
                assert(not widget:IsInViewport(),"original subview Close did not remove widget: " .. entry.class)
                pause:SetKeyboardFocus()
                return true
            end
        end
    end
    for _,widget in ipairs(FindAllOf("SettingsMaster_WBP_C") or {}) do
        if runtime.valid(widget) and widget:IsInViewport() and sameWorld(widget,pause) then
            original(widget,SETTINGS_CANCEL)
            assert(not widget:IsInViewport(),"original settings Cancel did not close subview")
            pause:SetKeyboardFocus()
            return true
        end
    end
    if not context:IsA(PAUSE) then return false end
    local overlay = pause.AreYouSureOverlay
    assert(runtime.valid(overlay),"pause confirmation overlay unavailable")
    local visibility = overlay:GetVisibility()
    if visibility==0 or visibility==3 or visibility==4 then
        original(pause,NO)
        assert(overlay:GetVisibility()==2,"original confirmation No did not collapse subview")
    else
        original(pause,CLOSE)
        assert(not pause:IsInViewport(),"original pause Close did not remove widget")
    end
    return true
end
assert(type(RegisterKeyBind)=="function" and type(ExecuteInGameThread)=="function" and Key.ESCAPE==27,"required fixed Escape keybind API unavailable")
local pending=false
local registered,cause=pcall(RegisterKeyBind,Key.ESCAPE,function()
    if not mod.store.values.enabled or pending then return end
    pending=true
    local queued,queueCause=xpcall(function()
        ExecuteInGameThread(function()
            local ok,failure=xpcall(function()
                assert(IsInGameThread(),"Escape return callback outside game thread")
                if not mod.store.values.enabled then return end
                local active=pauses()
                assert(#active<=1,"local pause menu ambiguous")
                local pause=active[1]
                if pause and closeTop(pause,pause) then mod:log("info","ESC used original menu return path") end
            end,debug.traceback)
            pending=false
            if not ok then mod:log("error","Escape return: "..tostring(failure));error(failure) end
        end)
    end,debug.traceback)
    if not queued then pending=false;mod:log("error","Escape dispatch: "..tostring(queueCause));error(queueCause) end
end)
if not registered then mod:log("error","Escape registration: "..tostring(cause));error(cause) end
mod:log("info","fixed Escape keybind registered; gameplay acceptance pending")
mod:observe("pause focus",function()
    local activePauses = pauses()
    local function focusable(widget)
        local address = widget:GetAddress()
        if not focused[address] then
            focused[address] = {widget=widget,original=widget.bIsFocusable}
            widget.bIsFocusable = true
        end
        return address
    end
    for _,pause in ipairs(activePauses) do
        local pauseAddress = pause:GetAddress()
        if mod.store.values.enabled then
            focusable(pause)
            local target = pause
            for _,class in ipairs(subviews) do
                for _,widget in ipairs(FindAllOf(class) or {}) do
                    if runtime.valid(widget) and widget:IsInViewport() and sameWorld(widget,pause) then
                        local visibility = widget:GetVisibility()
                        if visibility==0 or visibility==3 or visibility==4 then target=widget;break end
                    end
                end
                if target~=pause then break end
            end
            local address = focusable(target)
            if topFocus[pauseAddress]~=address then
                topFocus[pauseAddress] = address
                if not target:HasKeyboardFocus() and not target:HasFocusedDescendants() then target:SetKeyboardFocus() end
            end
        else
            topFocus[pauseAddress] = nil
        end
    end
    for address,record in pairs(focused) do
        if not mod.store.values.enabled or not runtime.valid(record.widget) or not record.widget:IsInViewport() then
            if runtime.valid(record.widget) then record.widget.bIsFocusable=record.original end
            focused[address]=nil
        end
    end
    for address in pairs(topFocus) do
        local found = false
        for _,pause in ipairs(activePauses) do if pause:GetAddress()==address then found=true;break end end
        if not found then topFocus[address]=nil end
    end
end)
return mod
