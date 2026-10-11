"""Exercise original Escape return paths with widget doubles, without claiming focus acceptance."""
from pathlib import Path
from lupa.lua54 import LuaRuntime

vm = LuaRuntime(unpack_returned_tuples=True)
source = Path(__file__).resolve().parents[1] / "Mods/CabinEscapeFix/Scripts/main.lua"
vm.globals().main_source = source.read_text(encoding="utf-8")
vm.globals().main_path = source.as_posix()
vm.execute('''
    objects={};keyName="Escape"
    function FindAllOf(class) return objects[class] or {} end
    mod={store={values={enabled=true}},hooks={},observers={},messages={}}
    function mod:bind(path,callback) self.hooks[path]=callback end
    function mod:observe(name,callback) self.observers[name]=callback end
    function mod:log(level,cause) self.messages[#self.messages+1]=cause end
    package.preload.cabin_runtime=function() return {start=function() return mod end,valid=function(v) return v and v:IsValid() end} end
    local world={};function world:GetAddress() return 7 end
    function widget(kind)
        local w={kind=kind,visible=true,focuses=0,calls=0}
        function w:IsValid() return true end;function w:IsInViewport() return self.visible end
        function w:GetWorld() return world end;function w:GetAddress() return 42 end
        function w:IsA(path) return self.kind=="pause" end
        function w:SetKeyboardFocus() self.focuses=self.focuses+1 end
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
    function StaticFindObject(path)
        if path:find("KismetInputLibrary",1,true) then return {IsValid=function() return true end,GetKey=function() return {KeyName={ToString=function() return keyName end}} end} end
        return {Handled=function() return "handled" end}
    end
    assert(load(main_source,"@"..main_path))()
    callback=mod.hooks["/Script/UMG.UserWidget:OnPreviewKeyDown"]
    context={get=function() return pause end};event={get=function() return {} end}
    assert(callback(context,nil,event)=="handled" and not pause.visible and pause.calls==1)
    pause.visible=true;overlay.visibility=0
    assert(callback(context,nil,event)=="handled" and pause.visible and overlay.visibility==2 and pause.calls==1)
    objects.SettingsMaster_WBP_C={settings}
    assert(callback(context,nil,event)=="handled" and pause.visible and not settings.visible and settings.calls==1 and pause.focuses==1)
    mod.store.values.enabled=false;assert(callback(context,nil,event)==nil and pause.calls==1)
    mod.store.values.enabled=true;keyName="Enter";assert(callback(context,nil,event)==nil and pause.calls==1)
''')
