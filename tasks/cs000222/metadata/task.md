# Mini-Project: Deep Learning for Computer Vision

## Background

The goal of the mini-project is for you to implement an entire deep learning pipeline yourself: data loading, model design, training, evaluation, and analysis. Rather than writing a paper about your work, you will turn in a Colab / Jupyter notebook that interleaves written explanations of your project with runnable source code and results, similar in structure to the homework assignments.

Your notebook should include the following sections:
- **Introduction**: Describe the problem you are trying to solve, why it is important or useful, and summarize any important pieces of prior work that you are building upon.
- **Dataset**: Describe the dataset or datasets you are working with. Show examples from the datasets. If you collected or constructed your own dataset, explain the process you used to collect the images and labels, and why you made the choices you did in the data collection process.
- **Method**: Describe the method you are using; this may also contain parts of the implementation of your model, loss function, or other components along with sanity checks to ensure that those components are correctly implemented, similar to the homework.
- **Experiments**: Describe the experiments you did, and key results that we requested for each project. This may interleave explanations of the experiments you run, code for running those experiments, and figures you generate as a result of those experiments.
- **Conclusion / Future work**: What did you learn in doing this project? What are the shortcomings or failure cases of your work? If you had more time or resources, how would you continue or expand upon the work you have already done?

You should structure your code similar to the homework assignments, where the vast majority of your implementation is in .py files and the notebook only contains minimal driver code that calls into functions implemented in .py files.

**Important**: You must run all cells in your notebook to receive credit – we will not rerun your notebook.

## Project Options

You may choose one of the following three project options:

### Option 1: Image Classification

#### Background
Of all the ideas we have discussed in the class, the most practically useful is image classification by transfer learning from a pretrained model. In this project you will build an image classification system as you might if faced with this problem in practice. You will collect your own image classification dataset, divide it into splits (train / val / test), and train classification models by transfer learning from networks pretrained on ImageNet.

#### Core Tasks

1. **Build an Image Classification Dataset**
   - Define a set of two or more categories into which you want to classify images (mutually exclusive categories are simpler)
   - Collect images and label them (at least 100 images per category)
   - Split dataset into train / val / test splits (suggested: 70% train, 10% val, 20% test)
   - Images should not come from an existing computer vision dataset

2. **Train an Image Classifier**
   - Use torchvision models (e.g., ResNet18, ResNet50, or RegNetY-400MF)
   - Compare three training approaches:
     - **Train from scratch**: Randomly initialize the model and train from scratch
     - **Feature extraction**: Initialize with ImageNet pretrained weights; extract features and train a linear model on top
     - **Fine-tuning**: Initialize with ImageNet pretrained weights; fine-tune the entire model
   - Train at least 6 different models
   - Experiment with different optimizers, learning rates, L2 regularization strengths, and data augmentation strategies
   - Show training curves (training loss per iteration, train and val accuracy per epoch)
   - Optionally try test-time augmentation or model ensembling

3. **Analyze your models**
   - Analyze at least two different models: your best-performing model and at least one other
   - Show qualitative examples of correctly and incorrectly classified images
   - Show confusion matrices (predicted category vs ground-truth category)
   - Use one or more attribution methods (e.g., Grad-CAM, saliency maps) to show what portions of images are used by the model for classification decisions

4. **Run on the test set**
   - Run your best-performing model on the test set
   - If performance differs significantly between val and test sets, explain why

#### Deliverables
- Create your own image classification dataset with at least 100 images per category. In your notebook, discuss the classification problem you chose to solve, and how you went about collecting the dataset. Show example images from the dataset.
- Train at least 6 different image classification models on your dataset; in your notebook, show training curves for each model (training loss, train and val accuracy during training). You should also include a table that summarizes the final train and val accuracies of all your models. You must include at least one transfer learning result (feature extraction or finetuning from a model pretrained on ImageNet) and at least one result where you train the same CNN architecture from scratch on your dataset.
- In your notebook, analyze at least two of your trained models by showing qualitative examples, confusion matrices, and results from at least one attribution method on several images.

#### Papers to Read
- Donahue et al, "DeCAF: A Deep Convolutional Activation Feature for Generic Visual Recognition", ICML 2014. [arXiv link](https://arxiv.org/abs/1310.1531)
- Razavian et al, "CNN Features off-the-shelf: an Astounding Baseline for Recognition", CVPR Workshops 2014. [arXiv link](https://arxiv.org/abs/1403.6382)
- Simonyan et al, "Deep Inside Convolutional Networks: Visualising Image Classification Models and Saliency Maps", ICLR Workshop 2014. [arXiv link](https://arxiv.org/abs/1312.6034)
- Selvaraju et al, "Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization", IJCV 2019. [arXiv link](https://arxiv.org/abs/1610.02391)
- Fong et al, "Understanding Deep Networks via Extremal Perturbations and Smooth Masks", ICCV 2019. [arXiv link](https://arxiv.org/abs/1910.08485)

### Option 2: Single-Image Super-Resolution

#### Background
In the task of single-image super-resolution, a network receives as input a low-resolution image and it produces as output a higher-resolution version of the image. This is in general an underspecified problem – there are many possible high-resolution images that could correspond to the same low-resolution image. However, by training on datasets of corresponding high- and low-resolution images, a neural network can learn priors about the visual world that let it predict a plausible high-resolution output for any low-resolution input.

#### Core Tasks

1. **Model Implementation**
   - Implement a fully convolutional network for single-image super-resolution
   - Input: low-resolution image of shape 3 x H x W
   - Output: high-resolution image of shape 3 x fH x fW where f is the super-resolution factor (typically f=2, f=3, or f=4)
   - Use convolution layers and upsampling layers (nearest-neighbor, bilinear upsampling, or transpose convolution)
   - Train models for at least two super-resolution factors (f=2 and one other of your choice)
   - Implement models similar to SRCNN or FSRCNN
   - Optionally implement SRGAN for higher perceptual quality

2. **Training**
   - Train on any image dataset (ImageNet, COCO, or General100 dataset)
   - Use YCbCr color space: transform image from RGB to YCbCr, network predicts high-resolution Y channel, Cb and Cr channels are upsampled using bicubic interpolation
   - Training loss compares predicted and ground-truth Y channels
   - Experiment with different optimizers, training losses, model architectures
   - Show results for at least two different model variants for each super-resolution factor

3. **Evaluation**
   - Evaluate on Set5 and Set14 datasets (use versions from [this GitHub repository](https://github.com/jbhuang0604/SelfExSR/tree/master/data))
   - Use PSNR and SSIM metrics (implementations from scikit-image)
   - Compare against bilinear and bicubic upsampling baselines
   - Your best model should outperform both baselines for all super-resolution factors
   - Performance targets:
     - Super-resolution factor 2: PSNR ≥ 34 on Set5
     - Super-resolution factor 3: PSNR ≥ 31 on Set5
     - Super-resolution factor 4: PSNR ≥ 29 on Set5

#### Deliverables
- Implement models for single-image super-resolution. You should train models for at least two different super-resolution factors (2x, 3x, or 4x). For each model you should show training curves (loss on the train set, and PSNR on a held-out val set over the course of training). For each model you should report performance on the Set5 and Set14 datasets using PSNR and SSIM.
- You should compare against bilinear and bicubic upsampling, and your model should outperform these baselines.
- For super-resolution factors 2x / 3x / 4x, you should achieve PSNR on Set5 of at least 34 / 31 / 29.
- You should show qualitative results: show the low-resolution image, ground-truth high-resolution image, and predicted high-resolution image from each method you consider (your models and bilinear / bicubic) for several examples from a held-out val set, as well as for each image in Set5.

#### Papers to Read
- **SRCNN**: Dong et al, "Image super-resolution using deep convolutional networks", TPAMI 2015. [arXiv link](https://arxiv.org/abs/1501.00092)
- **FSRCNN**: Dong et al, "Accelerating the super-resolution convolutional neural network", ECCV 2016. [arXiv link](https://arxiv.org/abs/1608.00367)
- **SRGAN**: Ledig et al, "Photo-Realistic Single Image Super-Resolution using a Generative Adversarial Network", CVPR 2017. [arXiv link](https://arxiv.org/abs/1609.04802)

### Option 3: Novel View Synthesis with NeRF

#### Background
In the task of novel view synthesis, your training set consists of a set of images of a scene where you know the camera parameters (intrinsic and extrinsic) for each image. Your goal is to build a model that can synthesize images showing the scene from new viewpoints unseen in the training set.

Neural Radiance Fields (NeRFs) have emerged as a simple and powerful model for this problem. NeRFs rely on the idea of volume rendering: to determine the color of a pixel, we shoot a ray originating from the camera center through the pixel and into the scene; for a set of points along the ray, we compute both the color and opacity of the 3D scene. Integrating the influence of these points gives the color of the pixel.

#### Core Tasks

1. **Model Implementation**
   - Re-implement the model from the original NeRF paper
   - Train a fully-connected neural network that inputs (x, y, z) coordinates and a viewing direction, and outputs the RGB color and opacity of the 3D scene at that point
   - Given computational constraints, consider simplifications:
     - **Smaller MLP**: Use a shallower or narrower model than the original 8-layer MLP with 256 hidden units per layer
     - **No hierarchical sampling**: Use only a coarse model instead of separate coarse and fine models
     - **Fewer samples per ray**: Use fewer than 64 coarse and 128 fine samples per ray
     - **Shorter training schedule**: Train with smaller batch size or fewer iterations than 100k-300k
     - **Lower resolution images**: Downsample images during training (by 2x, 4x, or 8x)
   - Optionally incorporate ideas from Mip-NeRF or novel ideas of your own design

2. **Training**
   - Train on datasets from the NeRF paper (available [here](https://www.matthewtancik.com/nerf))
   - Show training curves (training losses and PSNR on at least one image from a held-out val set)
   - Compare runtime and convergence speed for different model variants

3. **Evaluation**
   - Show results on at least two different scenes from the NeRF paper datasets
   - Evaluate using PSNR and SSIM on test-set images
   - Show qualitative results: ground-truth images and predicted images from both training set views and novel test-set views
   - Generate at least one video result showing images along a continuously moving camera path

#### Deliverables
- Re-implement the method from the NeRF paper. Rather than exactly re-implementing their method, you should use some of the suggested modifications (or others of your own design) above to try and reduce the training time. You should fully describe any changes you make to the basic NeRF algorithm.
- You should show results on at least two scenes used in the NeRF paper. For each scene, you should show training curves from your model (training losses and PSNR on at least one image from a held-out val set). You should also show qualitative results from each method: show several examples of a ground-truth image and your predicted image, both from training set views and novel test-set views.
- Show at least one video result, where you generate images along a continuously moving camera path, similar to the examples on the [NeRF project page](https://www.matthewtancik.com/nerf).

#### Papers to Read
- Mildenhall et al, "NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis", ECCV 2020. [arXiv link](https://arxiv.org/abs/2003.08934)
- Barron et al, "Mip-NeRF: A Multiscale Representation for Anti-Aliasing Neural Radiance Fields", ICCV 2021. [arXiv link](https://arxiv.org/abs/2103.13415)

## General Requirements

### Code Structure
- Structure your code similar to the homework assignments
- The vast majority of your implementation should be in .py files
- The notebook should only contain minimal driver code that calls into functions implemented in .py files

### Open Source Code Policy
While there are many open source implementations for the problems described, you should not use them for your implementation. You may refer to existing open-source implementations if you are confused about a specific detail, but you should neither import from nor copy code directly from existing implementations. Your implementation should only use:
- Standard libraries for scientific computing in Python (numpy, scipy, matplotlib)
- PyTorch and torchvision
- Libraries specifically mentioned in the descriptions for each project

### Submission
- Turn in a .zip file containing both your final notebook and all code you implemented
- Your zip file should not include your training dataset (that would make the file too big)
- You must run all cells in your notebook to receive credit – we will not rerun your notebook
- The written text and figures in your notebook should be similar in length to a 3-4 page paper, but there are no strict requirements on length
