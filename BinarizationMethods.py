import numpy as np
from ImageProcessor import ImageProcessor
from matplotlib import pyplot as plt

class BinarizationMethods:

    def threshold_otsu(hist):
        total_pixels = np.sum(hist)
        current_max, thresh = 0, 0
        sum_total = np.dot(np.arange(256), hist)
        sum_background, weight_background, weight_foreground = 0, 0, total_pixels
        
        for i in range(256):
            weight_background += hist[i]
            weight_foreground = total_pixels - weight_background
            
            if weight_background == 0 or weight_foreground == 0:
                continue
            
            sum_background += i * hist[i]
            mean_background = sum_background / weight_background
            mean_foreground = (sum_total - sum_background) / weight_foreground
            
            between_class_variance = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2
            
            if between_class_variance > current_max:
                current_max = between_class_variance
                thresh = i
        
        return thresh

    def threshold_global(image, thresh):
        image_gray = ImageProcessor.to_gray(image)
        if thresh == 'otsu':
            hist_values, bins = np.histogram(image_gray, bins=256, range=(0, 256))
            thresh = BinarizationMethods.threshold_otsu(hist_values)    
    
            # plt.figure(figsize=(8, 6))
            # plt.bar(bins[:-1], hist_values, color='b', width=7, align='center', alpha=0.25)
            # plt.axvline(x = thresh, color = 'red', linestyle = 'solid', linewidth = 2, label = f'порог по Оцу: {thresh}')
            # plt.legend()
            # plt.show()
        
        height, width = ImageProcessor.get_size(image_gray)
        result_image = np.zeros_like(image_gray)
        for y in range(0, height):
            for x in range(0, width):
                if image_gray[y, x] > thresh:
                    result_image[y, x] = 255

        return result_image

    def threshold_bernsen(image, window_size=15, contrast_threshold=15):
        gthresh = 128
        image_gray = ImageProcessor.to_gray(image)
        height, width = image_gray.shape
        padding = window_size // 2
        padded_image = np.pad(image_gray, pad_width=padding, mode='edge')
        
        result_image = np.zeros_like(image_gray, dtype=np.uint8)
        
        for y in range(padding, height + padding):
            for x in range(padding, width + padding):
                window = padded_image[y - padding:y + padding + 1, x - padding:x + padding + 1]
                
                i_max = np.max(window)
                i_min = np.min(window)
                
                i_mean = i_max / 2. + i_min / 2.
                
                if i_max - i_min   < contrast_threshold:
                    result_image[y - padding, x - padding] = 255 if i_mean < gthresh else 0
                else:
                    result_image[y - padding, x - padding] = 255 if image_gray[y - padding, x - padding] < i_mean else 0
        
        return result_image

    def threshold_niblack(image, window_size=15, k=0.2):
        image_gray = ImageProcessor.to_gray(image)
        height, width = ImageProcessor.get_size(image_gray)
        padding = window_size // 2
        padded_image = np.pad(image_gray, ((padding, padding), (padding, padding)), mode='edge')

        result_image = np.zeros_like(image_gray)

        for y in range(padding, height + padding):
            for x in range(padding, width + padding):
                window = padded_image[y - padding:y + padding + 1, x - padding:x + padding + 1]

                m = np.mean(window) 
                s = np.std(window)    

                threshold = m - k * s

                if image_gray[y - padding, x - padding] > threshold:
                    result_image[y - padding, x - padding] = 255

        return result_image

    def threshold_sauvola(image, window_size):
        image_gray = ImageProcessor.to_gray(image)
        height, width = ImageProcessor.get_size(image_gray)
        padding = window_size // 2
        padded_image = np.pad(image_gray, ((padding, padding), (padding, padding)), mode='edge')

        result_image = np.zeros_like(image)

        for y in range(padding, height + padding):
            for x in range(padding, width + padding):
                window = padded_image[y - padding:y + padding + 1, x - padding:x + padding + 1]

                m = np.mean(window)
                s = np.std(window)

                k = 0.2 
                R = 128 
                threshold = m* (1 + k * ((s / R) - 1))

                if image_gray[y - padding, x - padding] > threshold:
                    result_image[y - padding, x - padding] = 255

        return result_image

    def threshold_eikwel(image, r_size, R_size, count, eps):

        def check_mean(array):
            return np.mean(array) if array.size > 0 else None

        def replace_block(image, start_x, start_y, r_size, R_size, flag, eps):
            res = False
            to_black = False
            half_R = R_size // 2
            x_left_R = max(0, start_x - half_R)
            x_right_R = min(image.shape[1], start_x + half_R + r_size)
            y_left_R = max(0, start_y - half_R)
            y_right_R = min(image.shape[0], start_y + half_R + r_size)

            R_pixels = image[y_left_R:y_right_R, x_left_R:x_right_R].copy()
            gray_R_pixels = ImageProcessor.to_gray(R_pixels) 
            hist_values, bins = np.histogram(gray_R_pixels, bins=256, range=(0, 256))
            otsu_threshold = BinarizationMethods.threshold_otsu(hist_values)
            max_R_pixels = gray_R_pixels[gray_R_pixels >= otsu_threshold]
            min_R_pixels = gray_R_pixels[gray_R_pixels < otsu_threshold]

            mean_max_R_pixels = check_mean(max_R_pixels)
            mean_min_R_pixels = check_mean(min_R_pixels)
            mean_gray_R_pixels = check_mean(gray_R_pixels)

            if abs(0 - mean_gray_R_pixels) < abs(255 - mean_gray_R_pixels): to_black = True
            
            if (mean_max_R_pixels is None or mean_min_R_pixels is None): res = True
            elif (abs(mean_max_R_pixels - mean_min_R_pixels)) > eps: res = True
            
            if flag == False:
                x_left_r = start_x
                x_right_r = min(start_x + r_size, image.shape[1])
                y_left_r = start_y
                y_right_r = min(start_y + r_size, image.shape[0])
            else:
                x_right_r = start_x
                x_left_r = max(start_x - r_size, 0)
                y_left_r = start_y
                y_right_r = min(start_y + r_size, image.shape[0])

            r_pixels = image[y_left_r:y_right_r, x_left_r:x_right_r].copy()
            gray_r_pixels = ImageProcessor.to_gray(r_pixels)
        
            if res == True: binary_block = np.where(gray_r_pixels >= otsu_threshold, 255, 0).astype(np.uint8)
            elif to_black == True:
                gray_r_pixels[:] = 0
                binary_block = gray_r_pixels
            else:
                gray_r_pixels[:] = 255
                binary_block = gray_r_pixels

            if len(image.shape) == 3:  
                image[y_left_r:y_right_r, x_left_r:x_right_r] = np.repeat(binary_block[:, :, np.newaxis], 3, axis=2)
            else: 
                image[y_left_r:y_right_r, x_left_r:x_right_r] = binary_block

        height, width = ImageProcessor.get_size(image)
        cur_count = 0
        reverse = False

        for start_y in range(0, height, r_size):  
            if reverse:
                x_range = range(width, 0, -r_size)
            else:
                x_range = range(0, width, r_size)
            for start_x in x_range: 
                replace_block(image, start_x, start_y, r_size, R_size, reverse, eps)
                cur_count += 1
                if count != 0 and cur_count == count:
                    return
            reverse = not reverse
        
        return image