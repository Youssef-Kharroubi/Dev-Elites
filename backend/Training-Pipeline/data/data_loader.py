import os
import random
import shutil
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from .preprocess import preprocess_dataset

def split_dataset(input_dir, train_dir, val_dir, test_dir, train_split=0.8, val_split=0.1):
    """
    Split dataset into training, validation and test sets with 80-10-10 split

    Args:
        input_dir: Source directory containing the dataset
        train_dir: Destination directory for training data
        val_dir: Destination directory for validation data
        test_dir: Destination directory for test data
        train_split: Percentage of data for training (default: 0.8)
        val_split: Percentage of data for validation (default: 0.1)
    """
    for directory in [train_dir, val_dir, test_dir]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

    all_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            all_files.append(os.path.join(root, file))

    random.shuffle(all_files)

    total_files = len(all_files)
    train_size = int(total_files * train_split)
    val_size = int(total_files * val_split)

    train_files = all_files[:train_size]
    val_files = all_files[train_size:train_size + val_size]
    test_files = all_files[train_size + val_size:]

    def copy_files(file_list, dest_dir):
        for file_path in file_list:
            rel_path = os.path.relpath(file_path, input_dir)
            dest_path = os.path.join(dest_dir, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(file_path, dest_path)

    copy_files(train_files, train_dir)
    copy_files(val_files, val_dir)
    copy_files(test_files, test_dir)

    print(f"Dataset split completed:")
    print(f"Training files: {len(train_files)} ({train_split*100}%)")
    print(f"Validation files: {len(val_files)} ({val_split*100}%)")
    print(f"Test files: {len(test_files)} ({(1-train_split-val_split)*100}%)")

def get_data_generators(train_dir, val_dir, test_dir, batch_size=32):
    datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2
    )
    train_gen = datagen.flow_from_directory(train_dir, target_size=TARGET_SIZE, batch_size=batch_size,
                                            class_mode='binary', color_mode='grayscale')
    val_gen = datagen.flow_from_directory(val_dir, target_size=TARGET_SIZE, batch_size=batch_size,
                                          class_mode='binary', color_mode='grayscale')
    test_gen = datagen.flow_from_directory(test_dir, target_size=TARGET_SIZE, batch_size=batch_size,
                                           class_mode='binary', color_mode='grayscale')
    return train_gen, val_gen, test_gen