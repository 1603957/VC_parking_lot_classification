import segment
import numpy as np
import os
import cv2

if __name__ == "__main__":
# Guardamos las imagenes en la carpeta images
    loadImage = input('Desea cargar las imagenes? (S/cualquier tecla)')
    if (loadImage == 'S'):
        src = "images/2_change/"
        dst = "images/2/image"
        segment.loadImages(src, dst)
    else:
        pass



    # Creamos la imagen media de alguna carpeta
    meanImage = input(
        'Desea crear una imagen media de algun parquing? (S/cualquier tecla)')
    if (meanImage == 'S'):
        print('Parquings disponibles para crear una imagen media:')
        print('1) Parquing 1')
        print('2) Parquing 2')
        print('3) Parquing 3')
        optionMean = int(input("Seleccione un parquing: "))
        if (optionMean < 1 and optionMean > 3):
            print('Error: Opcion no disponible')
        else:
            srcMean = 'images/' + str(optionMean) + '/'
            dstMean = 'images/average/average' + str(optionMean) + '.jpg'
            segment.makeMean(srcMean, dstMean)
    else:
        pass

    H = np.load("homography/H1.npy")
    for im in os.listdir('images/1'):
        print(im+"\n")
        img = cv2.imread('images/1/'+im)
        imagen = cv2.warpPerspective(img,H,(1080,1080))
        cv2.imwrite("homography/"+im,imagen)

    H = np.load("homography/H1.npy")
    img = cv2.imread('background/image_base.jpg')
    imagen = cv2.warpPerspective(img,H,(1080,1080))
    cv2.imwrite("background/H_image_base.jpg",imagen)
