# WinFormsDesignerAccessibilizer
This NVDA addon makes the out of process WinForms designer in Visual Studio 2022 announce components as they are selected via the keyboard.
It's a workaround so a better solution can and should be implemented directly in Visual Studio but when that will happen, nobody knows.

When the design surface gain focus the addon initializes things and there's probably a delay before the currently selected component is announced so please be patient. I'm running this on an Intel iMac from 2018 running Windows 10 so perhaps your setup is a lot snappier so you won't notice it.

The keys that triggers announcements are Tab, Shift+Tab, Escape and the arrow keys.
You can use Ctrl+Alt+L to focus the Solution Manager and then hit Escape to bring focus to the design surface. If something gets stuck and no components are announced you can try shifting the focus from and then back to the design surface.
Another key that's useful is F4. It focuses the list of properties in the Property Editor. You can move to the toolbar with Shift+Tab and move between the buttons with left and right buttons. Another Shift+Tab will focus the Components combobox where the currently selected component is shown. You can use Alt+Down Arrow to open the list of components on the design surface and select one by pressing Enter.

The heart of this addon is monitoring the value of the Components combobox. When  the value change the new value is announced.