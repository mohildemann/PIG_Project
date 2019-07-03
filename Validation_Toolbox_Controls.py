#-------------------------------------------------------------------------------
# Name: Validation Toolbox
# Purpose: Validation of the controls for the Toolbox created in the Final
#          Project of Python Class
# Author:      Carlos
#
# Created:     03/07/2019
# Copyright:   (c) Carlos 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
from tkinter import *
from tkinter import messagebox

class ToolValidator(object):
  """Class for validating a tool's parameter values and controlling
  the behavior of the tool's dialog."""

  def __init__(self):
    """Setup arcpy and the list of tool parameters."""
    self.params = arcpy.GetParameterInfo()
    self.fcfield = (None, None)

  def initializeParameters(self):
    """Refine the properties of a tool's parameters.  This method is
    called when the tool is opened."""
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parameter
    has been changed."""

    if self.params[3].value == True:
      self.params[4].enabled = 1
      self.params[5].enabled = 1
    else:
      self.params[4].enabled = 0
      self.params[5].enabled = 0

    if self.params[1].value == "Other":
        self.params[2].enabled = 1
    else:
        self.params[2].enabled = 0

    if self.params[6].value == True:
      self.params[7].enabled = 1
    else:
      self.params[7].enabled = 0

    if self.params[8].value == True:
      self.params[9].enabled = 1
      self.params[9].filter.list = [val for val in
                                        sorted(
                                          set(
                                            row[0]
                                            for row in arcpy.da.SearchCursor(str(self.params[0].value), "tag_ident")
                                              )
                                           )
                                      ]
    else:
      self.params[9].enabled = 0

    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    return