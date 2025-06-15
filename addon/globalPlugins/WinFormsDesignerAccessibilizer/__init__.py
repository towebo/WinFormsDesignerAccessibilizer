import appModuleHandler
import globalPluginHandler


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		appModuleHandler.registerExecutableWithAppModule("devenv", "WinFormsDesignerAccessibilizer")

	def terminate(self, *args, **kwargs):
		super().terminate(*args, **kwargs)
		appModuleHandler.unregisterExecutable("devenv")
