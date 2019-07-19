#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import cv2.cv2 as cv2

import ubicacion as ubi
import conector as cn

from datetime import datetime as time

class CamServer():
    def __init__(self, nombre="", dbConfig={}):
        self.conf = {"frecCNN": 20} #Análisis en LAN: frames{fluido,delay}= 4{si,>4"} 7{si,<1"} 10{si,~0"}
        
            #   #Cantidad de ciclos del timer que la CNN no trabaja
            #   #Esto es para evitar lag
            #   self.FREC=20
            #   self.FRECUENCIA_CNN=self.FREC
            #   #Seteo cada cuanto tiempo se activará el timer
            #   self.fps=40
        self.nombre = nombre
        self.status = cn.Status.OFF
        self.source = cn.DBSource(self,dbConfig)
    ##TODO: chequear conexion correcta con BBDD
        #Procesa setup y estado suspend    
        self.processNewState(cn.Status.SUSPENDING)
        
    def setup(self):
        #obtiene configuración de servidor, salvo que no exista y toma la BASE
        newStatus, self.conf = self.source.readSvrInfo()
    ##TODO: chequear newStatus no es asignado
    ##TODO: chequear configuración cargada correctamente
        #obtiene configuración de cámaras (ip/url,ubicaciones)
        c = self.source.readCamInfo() ##debería indicar cams a buscar
        #obtiene estado de ubicaciones (útil al recuperar post falla)
        b = self.source.readOcupyState()
        
        self.cams = cn.Camaras(c,self.conf["CONN_TIMEOUT"],self.conf["CONN_CHECK_TIMEOUT"])
        #comprobar conexión de cámaras por primera vez
        self.cams.checkConn()
        self.ubicaciones = ubi.Ubicacion(b,self.cams)
        #iniciar red neuronal
        PATH_TO_CKPT = os.path.join('modelo_congelado','frozen_inference_graph.pb')
        PATH_TO_LABELS = os.path.join('configuracion', 'label_map.pbtxt')
        #PATH_TO_TEST_IMAGES_DIR = 'img_pruebas'
        #TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR, 'image{}.jpg'.format(i)) for i in range(1, 3) ]
        self.rn = ubi.RN(PATH_TO_CKPT,PATH_TO_LABELS,TEST_IMAGE_PATHS)
        
    def start(self):
        self.status = cn.Status.WORKING
    
    def suspend(self):
        self.status = cn.Status.SUSPENDED
    
    ''' Procesar nuevo estado de servidor (control externo)
    - Se recibe status=[STARTING,RESTARTING,SUSPENDING]
    - Se procesan funciones: setup, start, suspend
    - Solo procesa cuando el newStatus difiere del actual '''
    def processNewState(self, newStatus=cn.Status.OFF):
        if (self.status != newStatus):
            if (self.status == cn.Status.OFF 
                or newStatus == cn.Status.RESTARTING):
                #Recargar configuracion servidor
                self.setup() 
            if (self.status in [cn.Status.OFF,cn.Status.SUSPENDED]
                and newStatus in [cn.Status.STARTING,cn.Status.RESTARTING]):
                #iniciar servidor / comenzar reconocimiento
                self.start()
            if (self.status in [cn.Status.OFF,cn.Status.WORKING]
                and newStatus == cn.Status.SUSPENDING):
                #suspender servidor / detener reconocimiento
                self.suspend()

    def keyStop(self):
        #uso variable "estática" para nuevos llamados a la función
        if not hasattr(CamServer.keyStop,"exit") or not CamServer.keyStop.exit:
            CamServer.keyStop.exit = False
            if cv2.waitKey(25) & 0xFF == ord('q'):
                self.processNewState(cn.Status.SUSPENDING)
                CamServer.keyStop.exit = True
        return CamServer.keyStop.exit

    ''' Proceso background de servidor '''
    def runService(self):
        try:
            i = self.conf["frecCNN"]
            #bucle infinito (funciona en background como servicio)
            while not self.keyStop():
                self.cams.captureFrame()
                if (i < self.conf["frecCNN"]):
                    i += 1
                else:
                    i = 0 
                    print(i)
                    if(len(self.cams.frames)):
                        frame = self.cams.frames[0]
  ####                  rect = self.rn.detect(self.cams.frames, "personaSentada", 
  ####                                        float(self.conf["ppersona"]))
  ####                  self.ubicaciones.addDetection(rect)
  ####                  # cada N detecciones o X tiempo
  ####                      newstate = self.ubicaciones.evaluateOcupy()
  ####                     #Grabar en la base de datos
        except IOError as e:
            print("Error IOError que no capturado correctamente.")
            #print(time.now(), "Error abriendo socket: ", ipcamUrl)
        except cv2.error as e:
            print(time.now(), "Error CV2: ", e)
        #    if e.number == -138:
        #        print("Compruebe la conexión con '" + ipcamUrl + "'")
        #    else:
        #        print("Error: " + e.message)
        except KeyboardInterrupt as e:
            print(time.now(), "Detenido por teclado.")
            
    #    except BaseException as e:
    #        print(time.now(), "Error desconocido: ", e)

if __name__ == "__main__":
    serverName = "SVR1"
    dbConfig = {'user':"usher",
                'passwd':"usher101",
                'svr':"usher.sytes.net",
                'db':"usher_rec"}
    sys.path.append("..")
    rnConfig = [
                os.path.join('modelo_congelado', 'frozen_inference_graph.pb'),
                os.path.join('configuracion', 'label_map.pbtxt'),
                ]
    NUM_CLASSES = 90
    FRECUENCIA_CNN = 10 #Análisis en LAN: frames{fluido,delay}= 4{si,>4"} 7{si,<1"} 10{si,~0"}

    PATH_TO_TEST_IMAGES_DIR = 'img_pruebas'
    TEST_IMAGE_PATHS = [ os.path.join('img_pruebas', 'image{}.jpg'.format(i)) for i in range(1, 3) ]

    svr = CamServer(serverName, dbConfig) #(sourceDB|sourceFile)
    svr.runService()
else:
    print("Ejecutando desde ", __name__)