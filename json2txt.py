import json
import os
import glob
from tqdm import tqdm

#输入你的类别
Classes=["disguise","camouflage"]

def convert_poly_to_rect(coordinateList):
    X = [int(coordinateList[2 * i]) for i in range(int(len(coordinateList) / 2))]
    Y = [int(coordinateList[2 * i + 1]) for i in range(int(len(coordinateList) / 2))]

    Xmax = max(X)
    Xmin = min(X)
    Ymax = max(Y)
    Ymin = min(Y)
    flag = False
    if (Xmax - Xmin) == 0 or (Ymax - Ymin) == 0:
        flag = True
    return [Xmin, Ymin, Xmax - Xmin, Ymax - Ymin], flag


def convert_labelme_json_to_txt(json_path, img_path, out_txt_path):
    json_list = glob.glob(json_path + '/*.json')
    num = len(json_list)
    for json_path in tqdm(json_list):
        with open(json_path, "r") as f_json:
            json_data = json.loads(f_json.read())
        infos = json_data['shapes']
        if len(infos) == 0:
            continue
        img_w = json_data['imageWidth']
        img_h = json_data['imageHeight']
        image_name = json_data['imagePath']
        image_path = os.path.join(img_path, image_name)
        if not os.path.exists(img_path):
            print(img_path, 'is None!')
            continue
        txt_name = os.path.basename(json_path).split('.')[0] + '.txt'
        txt_path = os.path.join(out_txt_path, txt_name)
        f = open(txt_path, 'w')
        for label in infos:
            points = label['points']
            if len(points) < 2:
                continue

            if len(points) == 2:
                x1 = points[0][0]
                y1 = points[0][1]
                x2 = points[1][0]
                y2 = points[1][1]
                points = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
            else:
                if len(points) < 4:
                    continue

            segmentation = []
            for p in points:
                segmentation.append(int(p[0]))
                segmentation.append(int(p[1]))

            bbox, flag = convert_poly_to_rect(list(segmentation))
            x1, y1, w, h = bbox

            if flag:
                continue

            x_center = x1 + w / 2
            y_center = y1 + h / 2
            norm_x = x_center / img_w
            norm_y = y_center / img_h
            norm_w = w / img_w
            norm_h = h / img_h
            obj_cls = label['label']
            cls_id=Classes.index(obj_cls)
            line = [cls_id, norm_x, norm_y, norm_w, norm_h]
            line = [str(ll) for ll in line]
            line = ' '.join(line) + '\n'
            f.write(line)
        f.close()


if __name__ == "__main__":
    img_path = 'images' #图片路径
    json_path = 'json'  #json格式路径
    out_txt_path = 'try'    #txt格式路径

    if not os.path.exists(out_txt_path):
        os.makedirs(out_txt_path)

    convert_labelme_json_to_txt(json_path, img_path, out_txt_path)


