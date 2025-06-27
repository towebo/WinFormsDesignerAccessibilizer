# -*- coding: UTF-8 -*-
# Makes the Out Of Process WinForms designer in Visual Studio announce the selected components

import api
from ctypes import *
import appModuleHandler
from NVDAObjects.UIA import UIA
from NVDAObjects.window import Window
import UIAHandler
from NVDAObjects.IAccessible import IAccessible, ContentGenericClient, getNVDAObjectFromEvent
import speech
from scriptHandler import script
import ui
from logHandler import log
import windowUtils
import winUser
import eventHandler
import core


def _findDescendantObject(
    parentWindowHandle: int,
    controlId: int | None = None,
    className: str | None = None,
) -> Window | None:
    """
    Finds a window with the given controlId or class name,
    starting from the window belonging to the given parentWindowHandle,
    and returns the object belonging to it.
    """
    try:
        obj = getNVDAObjectFromEvent(
            windowUtils.findDescendantWindow(parentWindowHandle, controlID=controlId, className=className),
            winUser.OBJID_CLIENT,
            0,
        )
    except LookupError:
        obj = None
    return obj

def _getNVDAObjectByClassName(
    controlClassName: str,
    ) -> Window | None:
    ctrl = getNVDAObjectFromEvent(
        windowUtils.findDescendantWindow(api.getForegroundObject().windowHandle, className=controlClassName,),
        winUser.OBJID_CLIENT,
        0,
        )
    return ctrl

def findChildByName(parentObj, wantedName):
    for child in parentObj.children:
        if child.name == wantedName:
            return child
        result = findChildByName(child, wantedName)
        if result:
            return result
    return None


class AppModule(appModuleHandler.AppModule):

    def __init__(self, *args, **kwargs):
        super(AppModule, self).__init__(*args, **kwargs)
        

    def chooseNVDAObjectOverlayClasses(self, obj, clsList):
        try:
            if isinstance(obj, IAccessible) and obj.windowText == "DesignerView":
                clsList.insert(0, VSDesignerView)
        except Exception as e:
            log.info("Fel i chooseNVDAObjectOverlayClasses: %s" % e)
            ui.message("Fel i chooseNVDAObjectOverlayClasses: %s" % e)



class VSDesignerView(IAccessible):

    last_component = ""
    has_focus = False
    components_combo = None

    def initOverlayClass(self):
        try:
            ui.message("Designer Focused")
            # Ensure we get the relevant components combo in case we have multiple instances of Visual Studio running
            VSDesignerView.components_combo = None
            VSDesignerView.last_component =""
            self.ensure_components_combo()
            self.announce_current_component()
        except Exception as e:
            log.info("Fel i designer selected: %s" % e)
            ui.message("Fel i designer selected: %s" % e)

    def event_gainFocus(self):
        has_focus = true
        super().event_gainFocus()

    def event_loseFocus(self):
        has_focus = false
        super().event_loseFocus()

    def ensure_components_combo(self):
        if VSDesignerView.components_combo is None:
            try:
                VSDesignerView.components_combo = findChildByName(api.getForegroundObject(), "Components")
            except Exception as e:
                ui.message("Error when finding components combo: %s" % e)

    def announce_current_component(self):
        try:
            if VSDesignerView.components_combo is not None:
                val = VSDesignerView.components_combo.value
                if val != VSDesignerView.last_component:
                    VSDesignerView.last_component = val
                    ui.message(VSDesignerView.last_component)
            else:
                self.ensure_components_combo()
        except Exception as e:
            ui.message("Shit: %s" % e)

    @script(
        gesture="kb:tab"
    )
    def script_keyTab(self, gesture):
        try:
            if has_focus:
                core.callLater(100, self.announce_current_component)
            return false
        except Exception as e:
            ui.message("Error: %s" % e)

    @script(
        gesture="kb:shift+tab"
    )
    def script_keyShiftTab(self, gesture):
        try:
            if has_focus:
                core.callLater(100, self.announce_current_component)
            return false
        except Exception as e:
            ui.message("Error: %s" % e)

    @script(
        gesture="kb:escape"
    )
    def script_keyEscape(self, gesture):
        try:
            if has_focus:
                core.callLater(100, self.announce_current_component)
            return false
        except Exception as e:
            ui.message("Error: %s" % e)

    @script(
        gesture="kb:leftArrow"
    )
    def script_keyLeftArrow(self, gesture):
        try:
            if has_focus:
                ui.message("Lefti")
                core.callLater(100, self.announce_current_component)
            return false
        except Exception as e:
            ui.message("Error: %s" % e)

    @script(
        gesture="kb:upArrow"
    )
    def script_keyUpArrow(self, gesture):
        try:
            if has_focus:
                core.callLater(100, self.announce_current_component)
            return  false
        except Exception as e:
            ui.message("Error: %s" % e)

    @script(
        gesture="kb:rightArrow"
    )
    def script_keyRightArrow(self, gesture):
        try:
            if has_focus:
                core.callLater(100, self.announce_current_component)
            return false
        except Exception as e:
            ui.message("Error: %s" % e)

    @script(
        gesture="kb:downArrow"
    )
    def script_keyDownArrow(self, gesture):
        try:
            if has_focus:
                core.callLater(100, self.announce_current_component)
            return false
        except Exception as e:
            ui.message("Error: %s" % e)


    @script(
        # Translators: Gesture description
        description=_("Says current control in the property editor."),
        category=_("WinForms Designer Accessibilizer"),
        gesture="kb:NVDA+j"
    )
    def script_announce_selected_component(self, gesture):
        self.announce_current_component()
        return false

