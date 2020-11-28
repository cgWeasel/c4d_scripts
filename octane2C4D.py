"""
OctaneToC4d
v0.1

Written by Graeme McDougall for Painting Practice
Copyright: Painting Practice (www.paintingpractice.com)
Written for Cinema 4d R20.057

Name-US:OctaneToC4d
Description-US:Converts selected Octane materials to Cinema 4d materials, as best as possible
"""

import c4d
from c4d import documents

ID_OCTANE_MATERIAL = 1029501                                                      #Here we define more readable IDs for any integer IDs we are using
ID_OCTANE_IMAGE_TEXTURE = 1029508                                                 #To make our code more readable
ID_OCTANE_COLORCORRECTION = 1029512
ID_OCTANE_INVERT_TEXTURE = 1029514
ID_OCTANE_MULTIPLY_TEXTURE = 1029516
ID_OCTANE_MIXTEXTURE = 1029505
mainLayerId = 526336


def CheckSelection(doc, mats):                                                    #Checks selection & returns a list of only the Octane materials
    oct_mats = []                                                                 #Create an empty list, to later store any Octane materials
    if mats:                                                                      #If there are any materials selected...
        count  = len(mats)                                                        #...get how many
        for i in range(count):                                                    #for each one...
            if mats[i].GetType() == ID_OCTANE_MATERIAL:                           #...if it's an Octane material...
                oct_mats.append(mats[i])                                          #...add it to our list of Octane materials
    return oct_mats                                                               #Return the list of Ocatne mats

def GetTexture(doc, oct_mat, channel):                                            #Gets a filename from a particular channel of an Octane mat
    image_name = None                                                             #Create an empty variable to store the image name
    image_shader = oct_mat[channel]                                               #Check the texture link & load shader in variable image_tex
    if image_shader:                                                              #If one is found...
        shader_type = image_shader.GetType()                                      #...get it's type

        if shader_type == ID_OCTANE_MULTIPLY_TEXTURE:                             #If it's a multiply shader...
            image_shader = image_shader[c4d.MULTIPLY_TEXTURE1]                    #Get the first shader in it
            if image_shader:                                                      #If we found a shader of some sort
                shader_type = image_shader.GetType()                              #Load it's type into the tex_type variable

        if shader_type == ID_OCTANE_MIXTEXTURE:                                   #If it's a mix shader...
            image_shader = image_shader[c4d.MIXTEX_TEXTURE1_LNK]                  #Get the first shader in it
            if image_shader:                                                      #If we found a shader of some sort
                shader_type = image_shader.GetType()                              #Load it's type into the tex_type variable

        if shader_type == ID_OCTANE_COLORCORRECTION:                              #If it's a colour correction shader
            image_shader = image_shader[c4d.COLORCOR_TEXTURE_LNK]                 #Get the texture in it's texture link & replace the image_tex var
            if image_shader:                                                      #If we found a shader of some sort
                shader_type = image_shader.GetType()                              #Load it's type into the tex_type variable

        if shader_type == ID_OCTANE_INVERT_TEXTURE:                               #If it's an invert shader
            image_shader = image_shader[c4d.INVERT_TEXTURE]                       #Get the texture in it's texture link & replace the image_tex var
            if image_shader:                                                      #If we found a shader of some sort
                shader_type = image_shader.GetType()                              #Get it's type

        if shader_type == ID_OCTANE_IMAGE_TEXTURE:                                #If after checking all this, we have an image texture shader..
            image_name = image_shader[c4d.IMAGETEXTURE_FILE]                      #Read the filename into the image_link variable
            print image_name
    return image_name                                                             #Return the filename, if found

def ReAssign(doc, oct_mat, c4d_mat):                                              #Assigns the new Cinema 4D material to the texture tags
    obj_link = oct_mat[c4d.ID_MATERIALASSIGNMENTS]                                #Get the link list for the Octane Material's assignment
    link_count = obj_link.GetObjectCount()                                        #Get how many objects are in the link list
    for i in range(link_count):                                                   #For each of them...
        tex_tag = obj_link.ObjectFromIndex(doc, i)                                #Get the texture tag
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, tex_tag)                                 #Add an undo for the tex tag change
        tex_tag[c4d.TEXTURETAG_MATERIAL] = c4d_mat                                #Replace the Octane Material with the Cinema 4D material
        tex_tag.Message(c4d.MSG_CHANGE)                                           #update the tex tag

def RebuildMats(doc, oct_mats):                                                   #Rebuilds each Octane material as a Cinema 4D material
    c4d_mats = []                                                                 #Create an empty list where we store our new Cinema 4D mats
    count = len(oct_mats)                                                         #Get how many Octane mats we have
    for i in range(count):                                                        #For each one...
        oct_mat = oct_mats[i]                                                     #Read the Octane Material into the variable oct_mat
        c4d_mat = c4d.BaseMaterial(c4d.Mmaterial)                                 #Create a new Cinema 4D material
        name = oct_mat[c4d.ID_BASELIST_NAME]                                      #Read the Material's name from the Octane mat...
        c4d_mat[c4d.ID_BASELIST_NAME] = name                                      #...and name the c4d material the same

        diff_file = GetTexture(doc, oct_mat, c4d.OCT_MATERIAL_DIFFUSE_LINK)       #Get the texure filename from the diffuse channel
        if diff_file:                                                             #If we did find a texrure filename...
            diff_shader = c4d.BaseShader(c4d.Xbitmap)                             #...create a new empty bitmap shader...
            diff_shader[c4d.BITMAPSHADER_FILENAME] = diff_file                    #...and load the filename in there
            c4d_mat[c4d.MATERIAL_COLOR_SHADER] = diff_shader                      #Assign the bitmap shader to the material's colour channel...
            c4d_mat.InsertShader(diff_shader)                                     #...and insert it into the material

        opac_file = GetTexture(doc, oct_mat, c4d.OCT_MATERIAL_OPACITY_LINK)       #Get the texture filename from the opacity channel
        if opac_file:                                                             #If we found one...
            opac_shader = c4d.BaseShader(c4d.Xbitmap)                             #...create a new empty bitmap shader...
            opac_shader[c4d.BITMAPSHADER_FILENAME] = opac_file                    #...and load the filename in there
            c4d_mat[c4d.MATERIAL_ALPHA_SHADER] = opac_shader                      #Assign the bitmap shader to the material's alpha channel...
            c4d_mat.InsertShader(opac_shader)                                     #...and insert it into the material
            c4d_mat[c4d.MATERIAL_USE_ALPHA] = True                                #Activate the alpha channel

        normal_file = GetTexture(doc, oct_mat, c4d.OCT_MATERIAL_NORMAL_LINK)      #Get the texure filename from the normal channel...
        if normal_file:                                                           #If we found one...
            normal_shader = c4d.BaseShader(c4d.Xbitmap)                           #...create a new empty bitmap shader
            normal_shader[c4d.BITMAPSHADER_FILENAME] = normal_file                #...and load the filename in there
            c4d_mat[c4d.MATERIAL_NORMAL_SHADER] = normal_shader                   #Assign the bitmap shader to the material's mormal channel...
            c4d_mat.InsertShader(normal_shader)                                   #...and insert it into the material
            c4d_mat[c4d.MATERIAL_USE_NORMAL] = True                               #Activate the normal channel

        bump_file = GetTexture(doc, oct_mat, c4d.OCT_MATERIAL_BUMP_LINK)          #Get the texure filename from the normal channel...
        if bump_file:                                                             #If we found one...
            bump_shader = c4d.BaseShader(c4d.Xbitmap)                             #...create a new empty bitmap shader
            bump_shader[c4d.BITMAPSHADER_FILENAME] = bump_file                    #...and load the filename in there
            c4d_mat[c4d.MATERIAL_BUMP_SHADER] = bump_shader                       #Assign the bitmap shader to the material's mormal channel...
            c4d_mat.InsertShader(bump_shader)                                     #...and insert it into the material
            c4d_mat[c4d.MATERIAL_USE_BUMP] = True                                 #Activate the normal channel

        rough_file = GetTexture(doc, oct_mat, c4d.OCT_MATERIAL_ROUGHNESS_LINK)    #Get the texure filename from the roughness channel...
        if rough_file:                                                            #If we found one...
            rough_shader = c4d.BaseShader(c4d.Xbitmap)                            #...create a new empty bitmap shader
            rough_shader[c4d.BITMAPSHADER_FILENAME] = rough_file                  #...and load the filename in there
            c4d_mat[c4d.MATERIAL_USE_REFLECTION] = True                           #Activate the Reflectance channel
            c4d_mat[mainLayerId + c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION] = 2     #Change the Default Specular to a Beckmann type
            c4d_mat[mainLayerId + c4d.REFLECTION_LAYER_MAIN_SHADER_ROUGHNESS] = rough_shader
            c4d_mat.InsertShader(rough_shader)                                    #...and insert it into the material

        ReAssign(doc, oct_mat, c4d_mat)                                           #Assign the new Cinema material inplace of the Octane one

        c4d_mats.append(c4d_mat)                                                  #Add the new mat to our list of Cinema 4D materials
        doc.InsertMaterial(c4d_mat)                                               #Insert the Cinema 4D Material in the document
        doc.AddUndo(c4d.UNDOTYPE_NEW, c4d_mat)                                    #Add an undo step for the new material

    return


def main():
    my_doc = documents.GetActiveDocument()                                        #Get the active document
    my_mats = my_doc.GetActiveMaterials()                                         #Get the selected materials
    my_oct_mats = CheckSelection(my_doc, my_mats)                                 #Checks the selected mats & returns only the octane ones

    if my_oct_mats:                                                               #If we did find Octane materials...
        doc.StartUndo()                                                           #Start the undo chain
        RebuildMats(my_doc, my_oct_mats)                                          #...re-create them as Cinema 4D mats
        doc.EndUndo()                                                             #End the undo chain
        c4d.EventAdd()                                                            #Add an event



if __name__=='__main__':
    main()