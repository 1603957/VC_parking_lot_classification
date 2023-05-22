import cv2
import numpy as np

def automatic_detection(image):
    # Aplicar un suavizado a la imagen
    image_blur = cv2.GaussianBlur(image, (5, 5), 0)
    rows,cols = image_blur.shape
    image_cut = image_blur[400:int(rows*3/4),:]
    sum_l = np.zeros(cols)
    for i in range(cols):
        if sum(image_cut[:,i]) > 0:
            sum_l[i] = 255
        else:
            sum_l[i] = 0
    # Calcular la separación promedio entre vehículos
    separaciones_if = []
    long_coche_if = []
    separaciones = []
    long_coche = []
    pix_ant = 0
    inicio_b = 0
    final_b = 0
    inicio_n = 0
    final_n = 0
    c = False
    for pix_n in range(len(sum_l)):
        if sum_l[pix_n] != sum_l[pix_ant]:
            if sum_l[pix_n] == 255.0:
                inicio_b = pix_n
                final_n = pix_ant
            else:
                final_b = pix_ant
                long_coche_if.append([inicio_b,final_b])
                separaciones_if.append([inicio_n,final_n])
                inicio_n = pix_n
        pix_ant = pix_n
    separaciones_if.append([inicio_n,cols])
    separaciones_if = separaciones_if[1:]
    
    for ifin in separaciones_if:
        separaciones.append(abs(ifin[1]-ifin[0]))
    for ifin in long_coche_if:
        long_coche.append(abs(ifin[1]-ifin[0]))

    #separacion_promedio = np.mean(separaciones)
    long_promedio = np.mean(long_coche)

    # Establecer un umbral para determinar si una plaza está ocupada o libre
    umbral_ocupado = 0.75 * long_promedio

    # Determinar el estado de las plazas
    estado_plazas = []
    cont = 1
    for separacion in separaciones:
        if separacion > umbral_ocupado:
            if int(separacion/umbral_ocupado) > 1:
                for i in range(int(separacion/umbral_ocupado)):
                    estado_plazas.append(0)
            else:
                estado_plazas.append(0)
        else:
            estado_plazas.append(1)
    return estado_plazas