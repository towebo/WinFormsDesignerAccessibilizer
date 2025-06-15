# WinForms Designer Accessibilizer

This add-on makes the out of process WinForms designer in Visual Studio 2022 announce components as they are selected.
Because the WinForms designer isn't in the same process as Visual Studio screen readers are unable to work as expected. This add-on keeps an eye on the components combobox at the top of the property editor and when its value changes the new value is announced by NVDA.
As it is a workaround for making the designer accessible you need to be patient because we havbe to pass keystrokes along and wait before announcing anything.