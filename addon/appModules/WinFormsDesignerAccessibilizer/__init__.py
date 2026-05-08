# -*- coding: UTF-8 -*-
# Makes the Out Of Process WinForms designer in Visual Studio announce the selected components

import addonHandler
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
import controlTypes


addonHandler.initTranslation()

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

def findAllChildrenByName(parentObj, wantedName, results=None):
    if results is None:
        results = []

    try:
        children = parentObj.children
    except Exception:
        return results

    for child in children:
        try:
            if child.name == wantedName:
                results.append(child)
        except Exception:
            pass

        findAllChildrenByName(child, wantedName, results)

    return results


def findPropertyRow(propertiesTable, propertyName):
    try:
        children = propertiesTable.children
    except Exception:
        return None

    for child in children:
        try:
            if child.name == propertyName:
                return child
        except Exception:
            pass

    return None


def getPropertyValue(propertiesTable, propertyName):
    row = findPropertyRow(propertiesTable, propertyName)
    if row is None:
        return None

    try:
        row.setFocus()
    except Exception:
        pass

    try:
        for child in row.children:
            if getattr(child, "role", None) == controlTypes.Role.EDITABLETEXT:
                return getattr(child, "value", None)
    except Exception:
        pass

    return None
def getPropertyValueBySelectingRow(propertiesTable, propertyName):
    row = findPropertyRow(propertiesTable, propertyName)
    if row is None:
        return None

    try:
        row.setFocus()
    except Exception:
        pass

    # Give VS time to create the value editor.
    core.callLater(50, lambda: None)

    try:
        for child in row.children:
            value = getattr(child, "value", None)
            name = getattr(child, "name", None)

            if value:
                return value

            if name and name != propertyName:
                return name
    except Exception:
        pass

    return None


def findPropertiesPane(root):
    matches = findAllChildrenByName(root, "Properties")

    for obj in matches:
        try:
            if obj.role == controlTypes.Role.PANE:
                return obj
        except Exception:
            pass

    return None

def findPropertiesPane(root):
    matches = findAllChildrenByName(root, "Properties")

    for obj in matches:
        try:
            if obj.role == controlTypes.Role.PANE:
                if containsText(obj, "Location") or containsText(obj, "Size"):
                    return obj
        except Exception:
            pass

    return None

def getPropertyValueBySelectingRow(propertiesTable, propertyName):
    row = findPropertyRow(propertiesTable, propertyName)
    if row is None:
        return None

    try:
        row.setFocus()
    except Exception:
        pass

    # Give VS time to create the value editor.
    core.callLater(50, lambda: None)

    try:
        for child in row.children:
            value = getattr(child, "value", None)
            name = getattr(child, "name", None)

            if value:
                return value

            if name and name != propertyName:
                return name
    except Exception:
        pass

    return None

def selectPropertyRow(row):
    try:
        row.setFocus()
    except Exception:
        pass

    try:
        row.doAction()
    except Exception:
        pass

def getPropertyValueNoFocus(propertiesTable, propertyName):
    row = findPropertyRow(propertiesTable, propertyName)
    if row is None:
        return None

    try:
        for child in row.children:
            if getattr(child, "role", None) == controlTypes.Role.EDITABLETEXT:
                return getattr(child, "value", None)
    except Exception:
        pass

    return None

def dumpTree(obj, level=0, maxLevel=8):
    if obj is None or level > maxLevel:
        return

    try:
        log.info(
            "%srole=%r name=%r value=%r class=%r UIA=%r controlType=%r automationId=%r"
            % (
                "  " * level,
                getattr(obj, "role", None),
                getattr(obj, "name", None),
                getattr(obj, "value", None),
                getattr(obj, "windowClassName", None),
                isinstance(obj, UIA),
                getattr(obj, "UIAElement", None).cachedControlType if hasattr(obj, "UIAElement") else None,
                getattr(obj, "UIAElement", None).cachedAutomationID if hasattr(obj, "UIAElement") else None,
            )
        )
    except Exception as e:
        log.info("%sdump error: %s" % ("  " * level, e))

    # Normal NVDA children
    try:
        for child in obj.children:
            dumpTree(child, level + 1, maxLevel)
    except Exception:
        pass

    # UIA children
    try:
        elem = obj.UIAElement
        walker = UIAHandler.handler.clientObject.createTreeWalker(
            UIAHandler.handler.clientObject.createTrueCondition()
        )
        childElem = walker.GetFirstChildElement(elem)

        while childElem:
            childObj = UIA(UIAElement=childElem)
            dumpTree(childObj, level + 1, maxLevel)
            childElem = walker.GetNextSiblingElement(childElem)
    except Exception:
        pass

def dumpInteresting(obj, level=0, maxLevel=12):
    if obj is None or level > maxLevel:
        return

    try:
        name = getattr(obj, "name", "") or ""
        role = getattr(obj, "role", None)
        value = getattr(obj, "value", None)
        cls = getattr(obj, "windowClassName", "")
        controlType = None
        automationId = None

        if hasattr(obj, "UIAElement"):
            controlType = obj.UIAElement.cachedControlType
            automationId = obj.UIAElement.cachedAutomationID

        text = "%s role=%r name=%r value=%r class=%r controlType=%r automationId=%r" % (
            "  " * level,
            role,
            name,
            value,
            cls,
            controlType,
            automationId,
        )

        if (
            "Location" in name
            or "Size" in name
            or "Property" in name
            or "Properties" in name
            or "Grid" in name
            or "Location" in str(value)
            or "Size" in str(value)
        ):
            log.info(text)

    except Exception:
        pass

    try:
        for child in obj.children:
            dumpInteresting(child, level + 1, maxLevel)
    except Exception:
        pass

def findPropertiesWindow():
    # First try by visible name.
    return findChildByName(api.getForegroundObject(), "Properties")


def collectText(obj):
    parts = []

    try:
        if obj.name:
            parts.append(obj.name)
    except Exception:
        pass

    try:
        if obj.value:
            parts.append(obj.value)
    except Exception:
        pass
            
    return " ".join(parts)

def findPropertyValue(parentObj, propertyName):
    """
    Searches the accessible tree for a property row containing propertyName.
    This is intentionally heuristic because VS property grid structures vary.
    """
    try:
        children = parentObj.children
    except Exception:
        return None

    for child in children:
        text = collectText(child)
        if text == propertyName:
            # Common case: next sibling may contain the value.
            try:
                index = children.index(child)
                valueObj = children[index + 1]
                value = getattr(valueObj, "value", None) or getattr(valueObj, "name", None)
                if value:
                    return value
            except Exception:
                pass
                    
            # Sometimes row object contains both name and value.
            if propertyName in text:
                # Example: "Location 12, 34"
                cleaned = text.replace(propertyName, "", 1).strip()
                if cleaned:
                    return cleaned
                        
                result = findPropertyValue(child, propertyName)
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
    PROPERTIES_TO_REPORT = ("Location", "Size")

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
        self.has_focus = True
        super().event_gainFocus()

    def event_loseFocus(self):
        self.has_focus = False
        super().event_loseFocus()


    def announceLocationAndSize(self):
        propertiesTable = findChildByName(api.getForegroundObject(), "Properties Window")
        location = getPropertyValueNoFocus(propertiesTable, "Location")
        size = getPropertyValueNoFocus(propertiesTable, "Size")        
        
        messages = []
        if location:
            messages.append("Location %s" % location)
        if size:
            messages.append("Size %s" % size)
            
        if messages:
            ui.message(", ".join(messages))
        else:
            ui.message("Skit också. Location and size not found")


    def ensure_components_combo(self):
        if VSDesignerView.components_combo is None:
            try:
                VSDesignerView.components_combo = findChildByName(api.getForegroundObject(), "Components")
            except Exception as e:
                ui.message("Error when finding components combo: %s" % e)

    def announce_current_component(self):
        try:
            if VSDesignerView.components_combo is None:
                self.ensure_components_combo()
            if VSDesignerView.components_combo is None:
                return

            try:
                val = VSDesignerView.components_combo.value
            except Exception as e:
                    VSDesignerView.components_combo = None
                    self.ensure_components_combo()
                    return
            if val != VSDesignerView.last_component:
                VSDesignerView.last_component = val
                ui.message(VSDesignerView.last_component)
                # This doesn't work unless the property has been focused in the property editor first.
                #core.callLater(100, self.announceLocationAndSize)
            else:
                self.ensure_components_combo()
        except Exception as e:
            ui.message("Announce Current Component: %s" % e)

    @script(
        gesture="kb:tab"
    )
    def script_keyTab(self, gesture):
        try:
            gesture.send()
            if self.has_focus:
                core.callLater(100, self.announce_current_component)
        except Exception as e:
            ui.message("Error: %s" % e)

    @script(
        gesture="kb:shift+tab"
    )
    def script_keyShiftTab(self, gesture):
        try:
            gesture.send()
            if self.has_focus:
                core.callLater(100, self.announce_current_component)
        except Exception as e:
            ui.message("Error: %s" % e)

    @script(
        gesture="kb:escape"
    )
    def script_keyEscape(self, gesture):
        try:
            gesture.send()
            if self.has_focus:
                core.callLater(100, self.announce_current_component)
        except Exception as e:
            ui.message("Error: %s" % e)

    @script(
        gesture="kb:leftArrow"
    )
    def script_keyLeftArrow(self, gesture):
        try:
            gesture.send()
            if self.has_focus:
                core.callLater(100, self.announce_current_component)
        except Exception as e:
            ui.message("Error: %s" % e)

    @script(
        gesture="kb:upArrow"
    )
    def script_keyUpArrow(self, gesture):
        try:
            gesture.send()
            if self.has_focus:
                core.callLater(100, self.announce_current_component)
        except Exception as e:
            ui.message("Error: %s" % e)

    @script(
        gesture="kb:rightArrow"
    )
    def script_keyRightArrow(self, gesture):
        try:
            gesture.send()
            if self.has_focus:
                core.callLater(100, self.announce_current_component)
        except Exception as e:
            ui.message("Error: %s" % e)

    @script(
        gesture="kb:downArrow"
    )
    def script_keyDownArrow(self, gesture):
        try:
            gesture.send()
            if self.has_focus:
                core.callLater(100, self.announce_current_component)
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
        return False

