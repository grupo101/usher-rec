#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.3 on Thu Jun  6 17:54:54 2019
#

import wx
import time
import cv2
import numpy as np
import os
import sys
import tarfile
import tensorflow as tf
import zipfile
import collections
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
from datetime import datetime as time
from urllib.parse import urlparse
import glob
import xml.etree.ElementTree as ET
from collections import namedtuple
import socket
# Importación del módulo de detección de objetos.
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

import banca as banca

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        
        
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((812, 522))
        
        # Menu Bar
        self.frame_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        item = wxglade_tmp_menu.Append(wx.ID_ANY, u"Configuración", "")
        self.Bind(wx.EVT_MENU, self.configuraciónClick, id=item.GetId())
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Acerca de...", "")
        self.Bind(wx.EVT_MENU, self.acercaDeClick, id=item.GetId())
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Salir", "")
        self.Bind(wx.EVT_MENU, self.salirClick, id=item.GetId())
        self.frame_menubar.Append(wxglade_tmp_menu, "Menu")
        wxglade_tmp_menu = wx.Menu()
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Start/Stop", "")
        self.Bind(wx.EVT_MENU, self.cambiarEstadoCNN, id=item.GetId())
        self.frame_menubar.Append(wxglade_tmp_menu, "CNN")
        self.SetMenuBar(self.frame_menubar)
        # Menu Bar end
        self.label_1 = wx.StaticText(self, wx.ID_ANY, "Ubicaciones:")
        self.cantUbicaciones = wx.StaticText(self, wx.ID_ANY, "0")
        self.label_2 = wx.StaticText(self, wx.ID_ANY, "Ocupadas: ")
        self.cantOcupadas = wx.StaticText(self, wx.ID_ANY, "0")
        self.label_3 = wx.StaticText(self, wx.ID_ANY, "Libres:")
        self.cantLibres = wx.StaticText(self, wx.ID_ANY, "0")

        self.__set_properties()
        self.__do_layout()

        # end wxGlade
             

        #Create objects

        self.CaptureWidth = 640
        self.CaptureHeight = 480

        #Para Camara en vivo
        self.Screen1Width = 550
        self.Screen1Height = 300
        self.Screen1 = wx.StaticBitmap(self, size = (self.Screen1Width, self.Screen1Height)) # Static bitmaps for OpenCV images

        img = wx.Image('imagenes/bancaLibre.png').Scale(self.Screen1Width, self.Screen1Height, wx.IMAGE_QUALITY_HIGH)
        self.wxbmp = img.ConvertToBitmap()
        self.num=-1
        self.boxes=0
        self.scores=0
        self.classes=0
		
        self.sizer_2.Add( self.Screen1, 1, wx.FIXED_MINSIZE |wx.ALL, 5 )
                     
        self.Screen1.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)              
        self.Screen1.Bind(wx.EVT_PAINT, self.onPaint)

        # Add objects to sizer
        #self.sizer_2.Add(self.Screen1, 0, wx.EXPAND | wx.ALL, 10)

        #Para resultado del analisis
        self.Screen2Width = 550
        self.Screen2Height = 270
        
        #Maximizo ventana para que ocupe todo el escritorio menos la barra de tareas
        c_x, c_y, c_w, c_h = wx.ClientDisplayRect()
        self.SetSize((c_w, c_h))
        self.SetPosition((c_x, c_y))
        
        #Ventana mitad de escritorio
        self.SetSize((c_w/2, c_h))
        self.SetPosition((c_w/2, c_y))

  
        #Obtengo la posicion, dentro de la toma completa, de cada ubicacion 
        path_locations='configuracion'
        self.images_location=self.xml_to_locations(path_locations)
        self.cantUbicaciones.Label=str(len(self.images_location))
        self.cantLibres.Label=str(len(self.images_location))
        #Lista para guardar el estado de cada banca:
        # [OK] = ocupada
        # [ ] = libre
        # [?] = indeterminado
        self.locations_state=[]
         
        self.imagenes_bancas_select = { "ocupada": 'imagenes/bancaOcupadaSelect.png', "libre": 'imagenes/bancaLibreSelect.png', "indeterminado": 'imagenes/bancaIndeterminadoSelect.png' }

        #Creo tantas bancas como posiciones guardadas en el xml y las guardo en una lista
        #Las StaticBitmap contendran las imagenes de los estados de las bancas
        self.screen_list=[]
        for i in self.images_location:
           sb=wx.StaticBitmap(self, size = (self.Screen2Width, self.Screen2Height))
           #sb.SetPosition(wx.Point(0,0))  
           self.screen_list.append(banca.Banca(sb,i[0],i[1],i[2],i[3],i[4]))

        #Creo un diccionario para consultar datos de cada banca, al hacer click en una banca
        self.dict_bancas= {} # create an empty dictionary
        for i in range(len(self.screen_list)):
          self.dict_bancas[self.screen_list[i].staticBitmap]=self.screen_list[i]     
           
        

        #Seteo estado,posicion y evento de cada StaticBitmap
        for i in self.screen_list:

           #Seteo posicion proporcional al tamaño del screen y al tamaño de la captura
           xmin,ymin=i.getPosicionXML()
           xpos=int((xmin/self.CaptureWidth)*self.Screen2Width)
           ypos=int((ymin/self.CaptureHeight)*self.Screen2Height)
           x, y = self.sizer_3.GetPosition()
           i.setPosicionVentana(x+xpos,y+ypos)  

           #Seteo el eventos
           i.staticBitmap.Bind(wx.EVT_LEFT_UP, self.bancaClick)
           i.staticBitmap.Bind(wx.EVT_ENTER_WINDOW, self.onMouseOverBanca)
           i.staticBitmap.Bind( wx.EVT_LEAVE_WINDOW, self.onMouseOutBanca)

           #Seteo cursor sobre la banca
           i.staticBitmap.SetCursor(wx.Cursor(wx.CURSOR_HAND))

 
        ipcamUrl = 'http://admin:usher@192.168.1.33:8081'
        ipcam = {}
        ipcamDesc = 'Celular'
        ipcam[ipcamDesc] = urlparse(ipcamUrl)
        print(time.now())
        
        # Prueba la conexión al destino ip
        if len(ipcamUrl) > 5:
          err,errMsg = self.urlTest(ipcam[ipcamDesc].hostname,ipcam[ipcamDesc].port)
          if err > 0:
              print(time.now(),"Falló conexión. ",errMsg)
              exit(1)
        
        try:
          self.capture = cv2.VideoCapture(ipcamUrl)
          self.capture.set(3,self.CaptureWidth) #1024 640 1280 800 384
          self.capture.set(4,self.CaptureHeight) #600 480 960 600 288
          
        
          sys.path.append("..")
        
          # Importación del módulo de detección de objetos.
          from object_detection.utils import label_map_util
          from object_detection.utils import visualization_utils as vis_util
        
          PATH_TO_CKPT = 'modelo_congelado/frozen_inference_graph.pb'
        
          PATH_TO_LABELS = os.path.join('configuracion', 'label_map.pbtxt')
        
          NUM_CLASSES = 90
                  
          self.detection_graph = tf.Graph()
          with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
              serialized_graph = fid.read()
              od_graph_def.ParseFromString(serialized_graph)
              tf.import_graph_def(od_graph_def, name='')
        
        
          label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
          categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
          self.category_index = label_map_util.create_category_index(categories)
                          
        except IOError as e:
            print(time.now(), "Error abriendo socket: ", ipcamUrl)
        except KeyboardInterrupt as e:
            print(time.now(), "Detenido por teclado.")
        except BaseException as e:
            print(time.now(), "Error desconocido: ", e)
        #    if e.number == -138:
        #        print("Compruebe la conexión con '" + ipcamUrl + "'")
        #    else:
        #        print("Error: " + e.message)
        finally:
            #self.capture.release()
            cv2.destroyAllWindows()
        
        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph) as sess:
              self.sess = tf.Session()
              self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
              # Each box represents a part of the image where a particular object was detected.
              self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
              # Each score represent how level of confidence for each of the objects.
              # Score is shown on the result image, together with the class label.
              self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
              self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
              self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

              #Creo un timer para:
              # 1) Actualizar la información en pantalla
              # 2) Activar la CNN y obtener datos del analisis
              self.timer = wx.Timer(self)
              self.Bind(wx.EVT_TIMER, self.OnTimer)

              #Inicialmente la CNN está inactiva
              self.analisis=False

              
              self.Bind(wx.EVT_CLOSE, self.onClose)
              self.Bind(wx.EVT_LEFT_UP, self.VentanaClick)

              #Estado del programa
              self.STATE_RUNNING = 1
              self.STATE_CLOSING = 2
              self.state = self.STATE_RUNNING
              
              #Cantidad de ciclos del timer que la CNN no trabaja
              #Esto es para evitar lag
              self.FREC=20
              self.FRECUENCIA_CNN=self.FREC
                
              #Seteo cada cuanto tiempo se activará el timer
              self.fps=40
              self.timer.Start(1000./self.fps)    # timer interval
        
    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("USHER V1.0")
        self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, "Arial"))
        self.label_1.SetForegroundColour(wx.Colour(0, 0, 255))
        self.label_1.SetFont(wx.Font(12, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.cantUbicaciones.SetForegroundColour(wx.Colour(0, 0, 255))
        self.cantUbicaciones.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.label_2.SetForegroundColour(wx.Colour(0, 143, 57))
        self.label_2.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.cantOcupadas.SetForegroundColour(wx.Colour(0, 143, 57))
        self.cantOcupadas.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.label_3.SetForegroundColour(wx.Colour(204, 51, 51))
        self.label_3.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.cantLibres.SetForegroundColour(wx.Colour(203, 50, 53))
        self.cantLibres.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        self.sizer_1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "DASHBOARD"), wx.VERTICAL)
        self.sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Mapa de ubicaciones"), wx.VERTICAL)
        grid_sizer_1 = wx.GridBagSizer(0, 0)
        self.sizer_2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Cámara en vivo"), wx.VERTICAL)
        self.sizer_2.Add((0, 0), 0, 0, 0)
        self.sizer_1.Add(self.sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(30, 20, (0, 0), (1, 1), 0, 0)
        grid_sizer_1.Add(self.label_1, (0, 1), (1, 1), 0, 0)
        grid_sizer_1.Add(self.cantUbicaciones, (0, 2), (1, 1), 0, 0)
        grid_sizer_1.Add(30, 20, (0, 3), (1, 1), 0, 0)
        grid_sizer_1.Add(self.label_2, (0, 4), (1, 1), 0, 0)
        grid_sizer_1.Add(self.cantOcupadas, (0, 5), (1, 1), 0, 0)
        grid_sizer_1.Add(30, 20, (0, 6), (1, 1), 0, 0)
        grid_sizer_1.Add(self.label_3, (0, 7), (1, 1), 0, 0)
        grid_sizer_1.Add(self.cantLibres, (0, 8), (1, 1), 0, 0)
        self.sizer_3.Add(grid_sizer_1, 0, wx.TOP, 9)
        self.sizer_3.Add((0, 0), 0, 0, 0)
        self.sizer_1.Add(self.sizer_3, 1, wx.EXPAND, 0)
        self.SetSizer(self.sizer_1)
        self.Layout()
        # end wxGlade

    def OnTimer(self, event):
        
        ret, self.image_np = self.capture.read()
        
        if ret == True:
          #print("Captura OK")
          pass
        else:
          print("Falló la captura")
          exit(1)       

        if self.analisis==True:
          if self.FRECUENCIA_CNN==0: 
              # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
              image_np_expanded = np.expand_dims(self.image_np, axis=0)

              # Actual detection.      
              (self.boxes, self.scores, self.classes, self.num) = self.sess.run([self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],feed_dict={self.image_tensor: image_np_expanded})
              
              box = np.squeeze(self.boxes)
              #Alto del frame en pixeles
              height = np.size(self.image_np, 0)
              #Ancho del frame en pixeles
              width = np.size(self.image_np, 1)
              
              ##Comparo cada rectangulo del xml con cada box de la CNN
              ##Si el porcentaje de coincidencia es mayor a PORC_INTERSECCION guardo "[OK] "
              ##Si no, guardo "[ ] "
              self.locations_state=[]
              personas=0
              Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')
              PORC_INTERSECCION=0.3
              
              #Recorro las posiciones del xml
              for j in self.images_location:
                ymin = int(j[1])
                xmin = int(j[0])
                ymax = int(j[3])
                xmax = int(j[2])
                area_xml=(ymax-ymin)*(xmax-xmin)
                rxml = Rectangle(xmin, ymin, xmax, ymax)
                #Para cada posicion recorro las boxes buscando coincidencia
                coincide=False
                for index,value in enumerate(self.classes[0]):
                 if self.scores[0,index] > 0.3:
                   if self.category_index.get(value).get('name')=="person":
                     ymin = (int(box[index,0]*height))
                     xmin = (int(box[index,1]*width))
                     ymax = (int(box[index,2]*height))
                     xmax = (int(box[index,3]*width))
                     rbox = Rectangle(xmin, ymin, xmax, ymax)
                     area_interseccion=self.area(rxml, rbox)
                     if(area_interseccion!=None):
                       if area_interseccion>(PORC_INTERSECCION*area_xml):
                         coincide=True     
                      
                if coincide==True:
                  self.locations_state.append("[OK]")
                  personas+=1
                else:
                  self.locations_state.append("[ ]")
     
              print ("Se detectaron "+str(personas)+" personas\n")
              print (self.locations_state)
              print ("\n")
              
              self.cantOcupadas.Label=str(personas)
              self.cantLibres.Label=str(len(self.images_location)-personas)
              # Visualization of the results of a detection.
              vis_util.visualize_boxes_and_labels_on_image_array(
              self.image_np,
              np.squeeze(self.boxes),
              np.squeeze(self.classes).astype(np.int32),
              np.squeeze(self.scores),
              self.category_index,
              use_normalized_coordinates=True,
              line_thickness=4)
              self.FRECUENCIA_CNN=self.FREC
          else:
              self.FRECUENCIA_CNN-=1
        ###############################################
              
        #Indice para recorrer los estados actuales de las bancas
        estado=0

        imagenes_bancas = { "[OK]": 'imagenes/bancaOcupada.png', "[ ]": 'imagenes/bancaLibre.png', "[?]": 'imagenes/bancaIndeterminado.png' }
        nombres_estados_bancas = { "[OK]": "ocupada", "[ ]": "libre", "[?]": "indeterminado" }

        #Seteo estado,posicion de cada StaticBitmap
        for i in self.screen_list:

           #Seteo imagen
           if self.locations_state: #Si la lista no esta vacia
               i.setEstado(nombres_estados_bancas[self.locations_state[estado]]) 

               if i.getMouseEncima()==True:
                  imageFile = self.imagenes_bancas_select[i.getEstado()]
               else:
                  if i.getSeleccionado()==False:
                     imageFile = imagenes_bancas[self.locations_state[estado]]
                  else:
                     imageFile = self.imagenes_bancas_select[i.getEstado()]

           else:
               if i.getMouseEncima()==True:
                 imageFile = self.imagenes_bancas_select[i.getEstado()]
               else:
                 if i.getSeleccionado()==False:
                   imageFile = imagenes_bancas["[ ]"]
                 else:
                   imageFile = self.imagenes_bancas_select["libre"]

           i.setImagen(imageFile)
             
           #Seteo posicion proporcional al tamaño del screen y al tamaño de la captura
           separador=300
           xmin,ymin=i.getPosicionXML()
           xpos=int((xmin/(self.CaptureWidth-separador))*self.Screen2Width)-separador
           ypos=int((ymin/self.CaptureHeight)*self.Screen2Height)
           x, y = self.sizer_3.GetPosition()
           i.setPosicionVentana(x+xpos,y+ypos)  

           #if self.num!=-1:
           #  # Visualization of the results of a detection.
           #  vis_util.visualize_boxes_and_labels_on_image_array(
           #  self.image_np,
           #  np.squeeze(self.boxes),
           #  np.squeeze(self.classes).astype(np.int32),
           #  np.squeeze(self.scores),
           #  self.category_index,
           #  use_normalized_coordinates=True,
           #  line_thickness=4)

           #Dibujo rectangulo azul en camara de video indicando que ubicacion tengo apuntada con el mouse
           if i.getMouseEncima()==True:
                         
             vis_util.draw_bounding_box_on_image_array(
             self.image_np,
             i.yminXML,
             i.xminXML,
             i.ymaxXML,
             i.xmaxXML,
             color='red', #Color invertido, queda blue
             thickness=3,
             display_str_list= (str(i.nro)),
             use_normalized_coordinates=False)
           
           #Dibujo rectangulo rojo en camara de video indicando que ubicacion seleccione con el mouse
           if i.getSeleccionado()==True:
                         
             vis_util.draw_bounding_box_on_image_array(
             self.image_np,
             i.yminXML,
             i.xminXML,
             i.ymaxXML,
             i.xmaxXML,
             color='Blue', #Color invertido, queda red
             thickness=3,
             display_str_list= (str(i.nro)),
             use_normalized_coordinates=False)


           estado+=1



        self.image_np = cv2.cvtColor(self.image_np, cv2.COLOR_BGR2RGB) #Convert to RGB ready to display to screen
        self.image_np = cv2.resize(self.image_np, (self.Screen1Width, self.Screen1Height), interpolation = cv2.INTER_AREA) #Return a 320x240 RGB image
        h, w = self.image_np.shape[:2] # get the height and width of the source image for buffer construction
        self.wxbmp = wx.Bitmap.FromBuffer(w, h, self.image_np) # make a wx style bitmap using the buffer converter

        #self.Refresh()
        self.Screen1.Refresh()
        for i in range(len(self.screen_list)):
          self.screen_list[i].staticBitmap.Refresh()


        self.timer.Start(1000./self.fps)
        event.Skip()
         

    def configuraciónClick(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'configuraciónClick' not implemented!")
        event.Skip()

    def acercaDeClick(self, event):  # wxGlade: MyFrame.<event_handler>
        a=wx.MessageDialog(None,'USHER v1.0 \n Detección de personas con CNN \n\n PROYECTO FINAL 2019 \n Grupo 101','Acerca de',style=wx.OK)
        b=a.ShowModal()
        event.Skip()

    def salirClick(self, event):  # wxGlade: MyFrame.<event_handler>
        self.Close(True)
        event.Skip()

    def cambiarEstadoCNN(self, event):  # wxGlade: MyFrame.<event_handler>
        if self.analisis==True:
              self.analisis=False
        else:
          self.analisis=True
        event.Skip()
 # end of class MyFrame


    #Al cerrar la ventana paro el timer y elimino el frame
    def onClose(self, event):
        if not self.state == self.STATE_CLOSING:
            self.state = self.STATE_CLOSING
            self.timer.Stop()
            self.Destroy()    

    #Evento que se activa cuando se hace Refresh de algun StaticBitmap(Video o bancas)
    def onPaint(self, event):
       if self.state == self.STATE_RUNNING:
          #Se usa un buffer para evitar parpadeo de la imagen
          dc = wx.BufferedPaintDC(self.Screen1)
          dc.DrawBitmap(self.wxbmp, 0, 0)    
    
    #El fondo no se borra para evitar el parpadeo de la imagen
    def onEraseBackground(self, event):
        return        
        
    #Al hacer click sobre una banca, cambio el estado de seleccionado a todas las bancas
    def bancaClick(self, event): 
        
       #El metodo event.GetEventObject() devuelve el StaticBitmap clickeado
       #Mediante el StaticBitmap seleccionado consulto el diccionario dict_bancas StaticBitmap->Objeto banca   
       print("Hiciste click sobre la banca: "+str( self.dict_bancas[event.GetEventObject()].getNroBanca() ) ) 

       #Seteo todas las StaticBitmap des-seleccionadas
       for i in self.screen_list:
         self.dict_bancas[i.getStaticBitmap()].setSeleccionado(False)  

       #Seteo estado seleccionado True
       self.dict_bancas[event.GetEventObject()].setSeleccionado(True)   
  
       event.Skip()

    #Al hacer click sobre la ventana, cambio el estado de seleccionado False a todas las bancas
    def VentanaClick(self, event): 
        
       #Seteo todas las StaticBitmap des-seleccionadas
       for i in self.screen_list:
         self.dict_bancas[i.getStaticBitmap()].setSeleccionado(False)  

    #Al pasar el mouse sobre una banca
    def onMouseOverBanca(self, event): 
       
       #Seteo estado mouseEncima True
       self.dict_bancas[event.GetEventObject()].setMouseEncima(True) 

       event.Skip()

    #Al sacar el mouse de encima de una banca
    def onMouseOutBanca(self, event): 
  
       #Seteo estado mouseEncima False
       self.dict_bancas[event.GetEventObject()].setMouseEncima(False) 

       event.Skip()
    

    def urlTest(self,host, port):
        
        out = (0,"")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5.6)
        except socket.error as e:
            out = (1, "Error creating socket: %s" % e)
        # Second try-except block -- connect to given host/port
        else:
            try:
                s.connect((host, port))
            except socket.gaierror as e:
                out = (2, "Address-related error connecting to server: %s" % e)
            except socket.error as e:
                out = (3, "Connection error: %s" % e)
            finally:
                s.close()
        return out

    #A partir de un xml previamente cargado con labelImage, obtengo la posicion de cada ubicacion
    #(correspondiente a cada banca) dentro de la toma de video completa y el nro de banca
    def xml_to_locations(self,path):
        locations_list = []
        for xml_file in glob.glob(path + '/*.xml'):
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for member in root.findall('object'):
                value = (int(member[4][0].text), #xmin
                         int(member[4][1].text), #ymin
                         int(member[4][2].text), #xmax
                         int(member[4][3].text), #ymax
                         int(member[0].text), #nro banca                        
                         )
                locations_list.append(value)
        return locations_list
    
    #Area de interseccion entre 2 rectangulos
    #Para determinar coincidencia entre las posiciones del xml y las boxes de la CNN
    def area(self,a, b):  # returns None if rectangles don't intersect
        dx = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
        dy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
        if (dx>=0) and (dy>=0):
            return dx*dy
            
class MyApp(wx.App):

    def OnInit(self):
        
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
    
