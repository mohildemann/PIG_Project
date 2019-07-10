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

    #Case updating parameter related with gender
    if self.params[4].value == True and self.params[5].value == False and self.params[7].value == False:
      self.params[5].enabled = 0
      self.params[6].enabled = 0
      self.params[7].enabled = 0
      self.params[8].enabled = 0

    elif self.params[4].value == False and self.params[5].enabled == 0 and self.params[7].enabled == 0:
      self.params[4].enabled = 1
      self.params[5].enabled = 1
      self.params[7].enabled = 1
      self.params[4].value = False
      self.params[5].value = False
      self.params[7].value = False

    #Case updating paramter related with season
    elif self.params[4].value == False and self.params[5].value == True and self.params[7].value == False:
      self.params[6].enabled = 1
      self.params[4].enabled = 0
      self.params[7].enabled = 0
      self.params[8].enabled = 0

    elif self.params[4].enabled == 0 and self.params[5].value == False and self.params[7].enabled == 0:
      self.params[4].enabled = 1
      self.params[5].enabled = 1
      self.params[7].enabled = 1
      self.params[6].enabled = 0
      self.params[4].value = False
      self.params[5].value = False
      self.params[7].value = False

    #Case updating paramter related with id bird
    elif self.params[4].value == False and self.params[5].value == False and self.params[7].value == True:
      self.params[8].enabled = 1
      self.params[4].enabled = 0
      self.params[5].enabled = 0
      self.params[6].enabled = 0
      self.params[8].filter.list = [val for val in
                                        sorted(
                                          set(
                                            row[0]
                                            for row in arcpy.da.SearchCursor(str(self.params[0].value), "tag_ident")
                                              )
                                           )
                                      ]

    elif self.params[4].enabled == 0 and self.params[5].enabled == 0 and self.params[7].value == False:
      self.params[4].enabled = 1
      self.params[5].enabled = 1
      self.params[7].enabled = 1
      self.params[8].enabled = 0
      self.params[4].value = False
      self.params[5].value = False
      self.params[7].value = False

    else:
      self.params[4].value = False
      self.params[5].value = False
      self.params[7].value = False
      self.params[6].enabled = 0
      self.params[8].enabled = 0

    if self.params[2].value == "Other":
      self.params[3].enabled = 1
    else:
      self.params[3].enabled = 0


    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    #Messages for errors in the selection of the number to perform the buffer from the points
    if self.params[3].value is None and self.params[3].enabled == 1:
      self.params[2].setErrorMessage("Please provide a number to perform the analysis")
    else:
      self.params[2].clearMessage()

    #Messages for errors in the selection of the id of the birds
    if self.params[8].value is None and self.params[8].enabled == 1:
      self.params[7].setErrorMessage("Please select at least one id of the bird to perform the analysis")
    else:
      self.params[7].clearMessage()

    #Messages for errors in the selection of the season
    if self.params[6].value is None and self.params[6].enabled == 1:
      self.params[5].setErrorMessage("Please select at least one season to perform the analysis")
    else:
      self.params[5].clearMessage()
    return
