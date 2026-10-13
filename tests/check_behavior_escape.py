"""Exercise original Escape return paths with widget doubles, without claiming focus acceptance."""
from pathlib import Path
from lupa.lua54 import LuaRuntime

vm = LuaRuntime(unpack_returned_tuples=True)
source = Path(__file__).resolve().parents[1] / "Mods/CabinEscapeFix/Scripts/main.lua"
vm.globals().main_source = source.read_text(encoding="utf-8")
vm.globals().main_path = source.as_posix()
vm.execute('''
    objects={};gameThread=true;scheduled={};registrations=0;Key={ESCAPE=27}
    function IsInGameThread() return gameThread end
    function RegisterKeyBind(key,callback) assert(key==27);registrations=registrations+1;registeredKey=key;receiver=callback end
    function ExecuteInGameThread(callback) scheduled[#scheduled+1]=callback end
    function FindAllOf(class) return objects[class] or {} end
    mod={store={values={enabled=true}},hooks={},observers={},messages={}}
    function mod:bind(path,callback) self.hooks[path]=callback end
    function mod:observe(name,callback) self.observers[name]=callback end
    function mod:log(level,cause) self.messages[#self.messages+1]=cause end
    package.preload.cabin_runtime=function() return {start=function() return mod end,valid=function(v) return v and v:IsValid() end} end
    local world={};function world:GetAddress() return 7 end;function world:IsValid() return true end
    local player={localPlayer=true}
    function player:IsValid() return true end;function player:IsLocalController() return self.localPlayer end
    function player:GetWorld() assert(gameThread);return world end
    local nextAddress=40
    function widget(kind)
        nextAddress=nextAddress+1
        local w={kind=kind,visible=true,focuses=0,calls=0,address=nextAddress,bIsFocusable=false,keyboard=false,descendants=false,visibility=0}
        function w:IsValid() assert(gameThread);return true end;function w:IsInViewport() assert(gameThread);return self.visible end
        function w:GetWorld() assert(gameThread);return world end;function w:GetAddress() return self.address end
        function w:GetOwningPlayer() assert(gameThread);return player end
        function w:IsA(path) return self.kind=="pause" end
        function w:SetKeyboardFocus() self.focuses=self.focuses+1;self.keyboard=true end
        function w:HasKeyboardFocus() return self.keyboard end
        function w:HasFocusedDescendants() return self.descendants end
        function w:GetVisibility() return self.visibility end
        return w
    end
    pause=widget("pause");overlay={visibility=2}
    function overlay:IsValid() return true end;function overlay:GetVisibility() return self.visibility end
    pause.AreYouSureOverlay=overlay
    pause.BndEvt__WBP_Pause_Menu_Close_B_K2Node_ComponentBoundEvent_0_OnButtonPressedEvent__DelegateSignature=function(w) w.calls=w.calls+1;w.visible=false end
    pause.BndEvt__WBP_Pause_Menu_No_B_K2Node_ComponentBoundEvent_12_OnButtonPressedEvent__DelegateSignature=function(w) overlay.visibility=2 end
    settings=widget("settings")
    settings.BndEvt__SettingsMaster_WBP_Cancel_B_K2Node_ComponentBoundEvent_12_OnButtonPressedEvent__DelegateSignature=function(w) w.calls=w.calls+1;w.visible=false end
    objects.WBP_Pause_Menu_C={pause}
    assert(load(main_source,"@"..main_path))()
    assert(registrations==1 and next(mod.hooks)==nil,"only one keybind receiver; no old Preview hook")
    local function press(key)
        gameThread=false
        if key==registeredKey then receiver() end
        gameThread=true
    end
    local function flush()
        local actions=scheduled;scheduled={}
        for _,action in ipairs(actions) do action() end
    end
    press(27);assert(pause.visible and pause.calls==0 and #scheduled==1)
    press(27);assert(#scheduled==1,"pending dispatch must not double close")
    flush();assert(not pause.visible and pause.calls==1)
    pause.visible=true;overlay.visibility=0
    press(27);flush();assert(pause.visible and overlay.visibility==2 and pause.calls==1)
    objects.SettingsMaster_WBP_C={settings}
    press(27);flush();assert(pause.visible and not settings.visible and settings.calls==1 and pause.focuses==1)
    mod.store.values.enabled=false;press(27);assert(#scheduled==0 and pause.calls==1)
    mod.store.values.enabled=true;press(13);assert(#scheduled==0 and pause.calls==1)
    press(27);mod.store.values.enabled=false;flush();assert(pause.visible and pause.calls==1)
    mod.store.values.enabled=true
    objects.WBP_Pause_Menu_C={};settings.visible=true
    objects.CabinSettingsPanel_C={{visible=true}}
    press(27);flush();assert(settings.visible and settings.calls==1 and objects.CabinSettingsPanel_C[1].visible)
    objects.WBP_Pause_Menu_C={pause};player.localPlayer=false
    press(27);flush();assert(settings.visible and settings.calls==1)
    player.localPlayer=true
    local executor=ExecuteInGameThread
    function ExecuteInGameThread() error("fixture dispatch cause") end
    gameThread=false
    local queued,cause=pcall(receiver)
    gameThread=true
    assert(not queued and tostring(cause):find("fixture dispatch cause",1,true))
    ExecuteInGameThread=executor
    press(27);assert(#scheduled==1,"failed scheduling must release pending guard")
    mod.store.values.enabled=false;flush();mod.store.values.enabled=true
    local observe=mod.observers["pause focus"]
    pause.keyboard=false;settings.visible=true
    observe()
    assert(settings.bIsFocusable and settings.keyboard and settings.focuses==1 and pause.bIsFocusable)
    for i=1,100 do observe() end
    assert(settings.focuses==1)
    settings.keyboard=false;settings.descendants=true
    for i=1,100 do observe() end
    assert(settings.focuses==1,"observer must not steal keyboard focus from input descendants")
    local second=widget("settings");second.descendants=true
    settings.visible=false;objects.SettingsMaster_WBP_C={second}
    observe()
    assert(not settings.bIsFocusable and second.bIsFocusable and second.focuses==0)
    second.descendants=false;observe()
    assert(second.focuses==0,"same top identity must not refocus after descendant changes")
    local foreign=widget("bug");local otherWorld={GetAddress=function() return 99 end}
    function foreign:GetWorld() return otherWorld end
    objects.WBP_BugReport_C={foreign};observe()
    assert(not foreign.bIsFocusable and foreign.focuses==0)
    local credits=widget("credits");objects.WBP_Credits_C={credits};observe()
    assert(credits.bIsFocusable and credits.focuses==1 and second.focuses==0)
    local bug=widget("bug");objects.WBP_BugReport_C={foreign,bug};observe()
    assert(bug.bIsFocusable and bug.focuses==1 and credits.focuses==1)
    bug.visible=false;credits.visible=false;second.visible=false;objects.SettingsMaster_WBP_C={}
    pause.keyboard=false;observe()
    assert(pause.keyboard and pause.focuses==2 and not bug.bIsFocusable and not credits.bIsFocusable and not second.bIsFocusable)
    mod.store.values.enabled=false;observe()
    assert(not pause.bIsFocusable and not second.bIsFocusable)
    mod.store.values.enabled=true;settings.visible=true;settings.keyboard=false;settings.descendants=false
    objects.SettingsMaster_WBP_C={settings};observe()
    assert(settings.bIsFocusable and settings.focuses==2)
    mod.store.values.enabled=false;observe()
    assert(not settings.bIsFocusable and not pause.bIsFocusable)
    local registrar=RegisterKeyBind
    function RegisterKeyBind() error("fixture registration cause") end
    local loaded,registrationCause=pcall(assert(load(main_source,"@"..main_path)))
    assert(not loaded and tostring(registrationCause):find("fixture registration cause",1,true))
    RegisterKeyBind=registrar
    assert(registrations==1,"no registration retry or dual receiver")
''')
