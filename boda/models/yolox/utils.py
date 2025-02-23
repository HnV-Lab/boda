# import torch
# import torch.nn.functional as F
# import torchvision


# def preproc(img, input_size):
#     padded_img = torch.ones(3, input_size[0], input_size[1]) * 0.48
#     r = min(input_size[0] / img.shape[1], input_size[1] / img.shape[2])
#     resized_img = F.interpolate(
#         img[None],
#         size=(int(img.shape[1] * r), int(img.shape[2] * r)),
#         mode='bilinear',
#         align_corners=False
#     )[0]
#     print(resized_img.shape)
    
#     padded_img[:, :int(img.shape[1] * r), :int(img.shape[2] * r)] = resized_img
#     padded_img = padded_img.contiguous().type(torch.float32)

#     return padded_img, r


# def bboxes_iou(bboxes_a, bboxes_b, xyxy=True):
#     if bboxes_a.shape[1] != 4 or bboxes_b.shape[1] != 4:
#         raise IndexError

#     if xyxy:
#         tl = torch.max(bboxes_a[:, None, :2], bboxes_b[:, :2])
#         br = torch.min(bboxes_a[:, None, 2:], bboxes_b[:, 2:])
#         area_a = torch.prod(bboxes_a[:, 2:] - bboxes_a[:, :2], 1)
#         area_b = torch.prod(bboxes_b[:, 2:] - bboxes_b[:, :2], 1)
#     else:
#         tl = torch.max(
#             (bboxes_a[:, None, :2] - bboxes_a[:, None, 2:] / 2),
#             (bboxes_b[:, :2] - bboxes_b[:, 2:] / 2),
#         )
#         br = torch.min(
#             (bboxes_a[:, None, :2] + bboxes_a[:, None, 2:] / 2),
#             (bboxes_b[:, :2] + bboxes_b[:, 2:] / 2),
#         )

#         area_a = torch.prod(bboxes_a[:, 2:], 1)
#         area_b = torch.prod(bboxes_b[:, 2:], 1)
#     en = (tl < br).type(tl.type()).prod(dim=2)
#     area_i = torch.prod(br - tl, 2) * en  # * ((tl < br).all())
#     return area_i / (area_a[:, None] + area_b - area_i)


# def postprocess(prediction, num_classes, conf_thre=0.7, nms_thre=0.45, class_agnostic=False):
#     box_corner = prediction.new(prediction.shape)
#     box_corner[:, :, 0] = prediction[:, :, 0] - prediction[:, :, 2] / 2
#     box_corner[:, :, 1] = prediction[:, :, 1] - prediction[:, :, 3] / 2
#     box_corner[:, :, 2] = prediction[:, :, 0] + prediction[:, :, 2] / 2
#     box_corner[:, :, 3] = prediction[:, :, 1] + prediction[:, :, 3] / 2
#     prediction[:, :, :4] = box_corner[:, :, :4]

#     output = [None for _ in range(len(prediction))]
#     for i, image_pred in enumerate(prediction):

#         # If none are remaining => process next image
#         if not image_pred.size(0):
#             continue
#         # Get score and class with highest confidence
#         class_conf, class_pred = torch.max(image_pred[:, 5: 5 + num_classes], 1, keepdim=True)

#         conf_mask = (image_pred[:, 4] * class_conf.squeeze() >= conf_thre).squeeze()
#         # Detections ordered as (x1, y1, x2, y2, obj_conf, class_conf, class_pred)
#         detections = torch.cat((image_pred[:, :5], class_conf, class_pred.float()), 1)
#         detections = detections[conf_mask]
#         if not detections.size(0):
#             continue

#         if class_agnostic:
#             nms_out_index = torchvision.ops.nms(
#                 detections[:, :4],
#                 detections[:, 4] * detections[:, 5],
#                 nms_thre,
#             )
#         else:
#             nms_out_index = torchvision.ops.batched_nms(
#                 detections[:, :4],
#                 detections[:, 4] * detections[:, 5],
#                 detections[:, 6],
#                 nms_thre,
#             )

#         detections = detections[nms_out_index]
#         if output[i] is None:
#             output[i] = detections
#         else:
#             output[i] = torch.cat((output[i], detections))
          
#     output = [{
#         'boxes': o[:, :4],
#         'labels': o[:, 6],
#         'scores': o[:, 4] * o[:, 5],
#     } for o in output]
            
#     return output
