# GUI Setup
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from keras.preprocessing.image import load_img

root = Tk()
root.title('CadenceTrend')
root.attributes('-fullscreen', True)
Label(root, text="Welcome to Cadence Trend", font=('ALGERIAN BOLD', 27), bg='white', fg='black').place(x=550, y=10)

def logout():
    root.destroy()

def openfn():
    filename = filedialog.askopenfilename(title='open')
    return filename

def Img_Dec():
    filename = openfn()
    img = Image.open(filename)
    img = img.resize((250, 250), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)
    panel = Label(root, image=img)
    panel.image = img
    panel.place(x=80, y=220, width=350, height=350)

btn_upload = Button(root, text="Upload Image", font=("ALGERIAN", 14, "bold"), bg="Black", fg="white", command=Img_Dec, cursor="hand2")
btn_upload.place(x=80, y=600)

Button(text='EXIT', command=logout).place(x=700, y=800)

# -----------------------------------------------
# Image Captioning Code

import os
import pickle
import numpy as np
from tqdm import tqdm
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, LSTM, Embedding, Dropout, add
from tensorflow.keras.preprocessing.image import load_img, img_to_array

BASE_DIR = "D:/APTECH/Python/AI-PPT_19APRIL'25/archive (1)"
WORKING_DIR = BASE_DIR
IMAGE_DIR = os.path.join(BASE_DIR, 'Images')

# Extract VGG16 features
vgg_model = VGG16()
model_vgg = Model(vgg_model.inputs, vgg_model.layers[-2].output)

features = {}
for img_name in tqdm(os.listdir(IMAGE_DIR)):
    img_path = os.path.join(IMAGE_DIR, img_name)
    image = load_img(img_path, target_size=(224, 224))
    image = img_to_array(image)
    image = tf.expand_dims(image, axis=0)
    image = preprocess_input(image)
    feature = model_vgg.predict(image, verbose=0)
    image_id = img_name.split('.')[0]
    features[image_id] = feature

pickle.dump(features, open(os.path.join(WORKING_DIR, 'features.pkl'), 'wb'))

# Load features
with open(os.path.join(WORKING_DIR, 'features.pkl'), 'rb') as f:
    features = pickle.load(f)

# Load captions
with open(os.path.join(BASE_DIR, 'captions.txt'), 'r') as f:
    next(f)
    captions_doc = f.read()

mapping = {}
for line in tqdm(captions_doc.strip().split('\n')):
    tokens = line.split(',')
    if len(tokens) < 2:
        continue
    image_id = tokens[0].split('.')[0]
    caption = " ".join(tokens[1:]).strip()
    mapping.setdefault(image_id, []).append(caption)

def clean(mapping):
    for key, captions in mapping.items():
        for i in range(len(captions)):
            caption = captions[i].lower()
            caption = ' '.join([word for word in caption.split() if word.isalpha()])
            captions[i] = 'startseq ' + caption + ' endseq'

clean(mapping)

# Tokenizer
all_captions = [caption for captions in mapping.values() for caption in captions]
tokenizer = Tokenizer()
tokenizer.fit_on_texts(all_captions)
vocab_size = len(tokenizer.word_index) + 1
max_length = max(len(caption.split()) for caption in all_captions)

# Train-Test Split
image_ids = list(mapping.keys())
train = image_ids[:int(0.9 * len(image_ids))]
test = image_ids[int(0.9 * len(image_ids)):]

def data_generator(data_keys, mapping, features, tokenizer, max_length, vocab_size, batch_size):
    X1, X2, y = list(), list(), list()
    n = 0
    while True:
        for key in data_keys:
            captions = mapping[key]
            for caption in captions:
                seq = tokenizer.texts_to_sequences([caption])[0]
                for i in range(1, len(seq)):
                    in_seq, out_seq = seq[:i], seq[i]
                    in_seq = pad_sequences([in_seq], maxlen=max_length)[0]
                    out_seq = to_categorical([out_seq], num_classes=vocab_size)[0]
                    X1.append(features[key][0])
                    X2.append(in_seq)
                    y.append(out_seq)
            n += 1
            if n == batch_size:
                yield [np.array(X1), np.array(X2)], np.array(y)
                X1, X2, y = list(), list(), list()
                n = 0

# Define model
inputs1 = Input(shape=(4096,))
fe1 = Dropout(0.4)(inputs1)
fe2 = Dense(256, activation='relu')(fe1)

inputs2 = Input(shape=(max_length,))
se1 = Embedding(vocab_size, 256, mask_zero=True)(inputs2)
se2 = Dropout(0.4)(se1)
se3 = LSTM(256)(se2)

decoder1 = add([fe2, se3])
decoder2 = Dense(256, activation='relu')(decoder1)
outputs = Dense(vocab_size, activation='softmax')(decoder2)

model = Model(inputs=[inputs1, inputs2], outputs=outputs)
model.compile(loss='categorical_crossentropy', optimizer='adam')

# Train
epochs = 40
batch_size = 32
steps = len(train) // batch_size

for i in range(epochs):
    generator = data_generator(train, mapping, features, tokenizer, max_length, vocab_size, batch_size)
    model.fit(generator, epochs=1, steps_per_epoch=steps, verbose=1)

# Launch GUI
root.mainloop()
