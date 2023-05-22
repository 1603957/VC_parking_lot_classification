import segment
import set_regions
import paint_regions
import os
import numpy as np
import pickle
import automatic_detection
import cv2

chooseType = 'n'
len_auto = 6

if __name__ == "__main__":
    # Imagenes del parquing, img1 parking vacio, img2 parking con vehiculos
   
    print('Parquings disponibles:')
    print('0) Parquing 0')
    print('1) Parquing 1')
    print('2) Parquing 2')
    print('3) Parquing 3')
    print()

    option = int(input("Seleccione un parquing: "))
    if (option == 0):
        img1 = 'background/base_0.jpg'
        img2 = 'images/0/image1.jpg'
        dirPath = 'images/0'
        groundtruth_path = 'groundtruth/p0.txt'
        print('Parquing 0 seleccionado')
    elif (option == 1):
        img1 = 'background/base_1.jpg'
        img2 = 'images/1/image01.jpg'
        dirPath = 'images/1'
        groundtruth_path = 'groundtruth/p1.txt'
        print('Parquing 1 seleccionado')
    elif (option == 2):
        img1 = 'background/base_2.jpg'
        img2 = 'images/2/image01.jpg'
        dirPath = 'images/2'
        groundtruth_path = 'groundtruth/p2.txt'
        print('Parquing 2 seleccionado')
    elif (option == 3):
        img1 = 'background/base_3.jpg'
        img2 = 'images/3/image01.jpg'
        dirPath = 'images/3'
        groundtruth_path = 'groundtruth/p3.txt'
        print('Parquing 3 seleccionado')
    else:
        print('Error: Opcion no disponible')

    # Depende del parking a utilizar se cambia el nombre de H si usamos una homografia
    if (option == 1):
        chooseType = input('Desea utilizar una homografia? (S/cualquier tecla)')
        if (chooseType == 'S'):
            dirPath = 'images/homography'
            file = "homography/H" + str(option) + ".npy"
            if (os.path.isfile(file)):
                homography = input(
                    'Desea cargar una homografia existente? (S/cualquier tecla)')
                if (homography == 'S'):
                    H = np.load(file)
                    img_res, img2 = segment.segmentImagePerspective(
                        img1, img2, H=H, file=file)
                else:
                    img_res, img2 = segment.segmentImagePerspective(
                        img1, img2, H=np.array(None), file=file)
            else:
                img_res, img2 = segment.segmentImagePerspective(
                    img1, img2, H=np.array(None), file=file)
            img1 = "background/base_1_H.jpg"
        else:
            img_res = segment.segmentImage(img1, img2)

    # Los puntos de cada plaza de los parquings
    if (chooseType == 'S'):
        path = "regions/homography/region" + str(option) + ".p"
        groundtruth_path = 'groundtruth/p1H.txt'
    else:
        path = "regions/region" + str(option) + ".p"

    # Marcar las plazas existentes
    regions = input('Desea especificar las plazas? (S/cualquier tecla)')
    if (regions == 'S'):
        set_regions.setRegions(img1, path)
    else:
        pass

    # Guardamos las coordenadas
    with open(path, "rb") as f:
        coords = pickle.load(f)
    
    GT_list = []
    manual_list = []
    auto_list = []
    with open(groundtruth_path) as file:
        for line in file:
            GT_line = []
            for col in line:
                if col == '1' or col == '0':
                    GT_line.append(int(col))
            GT_list.append(GT_line)
    
    for im,GT in zip(os.listdir(dirPath),GT_list):
        img_res = segment.segmentImage(img1, dirPath+'/'+im)
        # Marcamos las plazas libres y ocupadas
        vehicle = segment.calculateLots(coords, img_res, img1, dirPath+'/'+im) # manual
        accuracy_manual = 0
        accuracy_auto = 0
        for i in range(len(vehicle)):
            if vehicle[i] == GT[i]:
                accuracy_manual = accuracy_manual + 1
        accuracy_manual = accuracy_manual/len(vehicle)
        manual_list.append(accuracy_manual)
        print(f"manual: {np.mean(accuracy_manual)}")
        
        if option == 0:
            auto_vehicle = automatic_detection.automatic_detection(img_res) # automatico
            for i in range(len(auto_vehicle)):
                if i >= len_auto:
                    break
                if auto_vehicle[i] == GT[i]:
                    accuracy_auto = accuracy_auto + 1
            accuracy_auto = accuracy_auto/len_auto
            auto_list.append(accuracy_auto)
            print(f"auto: {np.mean(accuracy_auto)}")

        # Pintamos las plazas de color verde si estan vacias o rojo si estan ocupadas
        paint_regions.paintRegions(dirPath+'/'+im, path, vehicle)
    print(f"manual: {np.mean(manual_list)}\n")
    if option == 0:
        print(f"auto: {np.mean(auto_list)}")



