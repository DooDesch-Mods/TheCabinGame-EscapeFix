local directory = assert(debug.getinfo(1,"S").source:match("^@(.+[/\\])"))
package.path = directory .. "?.lua;" .. package.path
local runtime = require("cabin_runtime")
local mod = runtime.start(directory,require("definition"))
local PAUSE = "/Game/CabinGameContent/HUD/WBP_Pause_Menu.WBP_Pause_Menu_C"
local CLOSE = "BndEvt__WBP_Pause_Menu_Close_B_K2Node_ComponentBoundEvent_0_OnButtonPressedEvent__DelegateSignature"
local NO = "BndEvt__WBP_Pause_Menu_No_B_K2Node_ComponentBoundEvent_12_OnButtonPressedEvent__DelegateSignature"
local SETTINGS_CANCEL = "BndEvt__SettingsMaster_WBP_Cancel_B_K2Node_ComponentBoundEvent_12_OnButtonPressedEvent__DelegateSignature"
local focused = {}
local function pauses()
    local result = {}
    for _,widget in ipairs(FindAllOf("WBP_Pause_Menu_C") or {}) do
        if runtime.valid(widget) and widget:IsInViewport() and widget:IsA(PAUSE) then result[#result+1]=widget end
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
mod:bind("/Script/UMG.UserWidget:OnPreviewKeyDown",function(context,geometry,keyEvent)
    if not mod.store.values.enabled then return end
    local widget = context:get()
    if not runtime.valid(widget) then return end
    local input = StaticFindObject("/Script/Engine.Default__KismetInputLibrary")
    assert(runtime.valid(input),"input library unavailable")
    local key = input:GetKey(keyEvent:get())
    if key.KeyName:ToString()~="Escape" then return end
    for _,pause in ipairs(pauses()) do
        if sameWorld(widget,pause) and closeTop(pause,widget) then
            mod:log("info","ESC used original menu return path")
            return StaticFindObject("/Script/UMG.Default__WidgetBlueprintLibrary"):Handled()
        end
    end
end)
mod:observe("pause focus",function()
    for _,pause in ipairs(pauses()) do
        local address = pause:GetAddress()
        local record = focused[address]
        if mod.store.values.enabled and not record then
            record = {widget=pause,original=pause.bIsFocusable}
            focused[address] = record
            pause.bIsFocusable = true
            pause:SetKeyboardFocus()
        elseif not mod.store.values.enabled and record then
            pause.bIsFocusable = record.original
            focused[address] = nil
        end
    end
    for address,record in pairs(focused) do
        if not runtime.valid(record.widget) or not record.widget:IsInViewport() then focused[address]=nil end
    end
end)
return mod
