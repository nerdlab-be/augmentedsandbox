% Run to obtain fft's from Europe.

clear all;
close all;
clc;

%%
[A,cmap,R] = geotiffread('elevation1x1_new.tif');
R.CoordinateSystemType = 'geographic';
figure
mapshow(A,R);
axis image off

Z = A(2000:2015, 2000:2015);
figure; surf(Z);
%%
N = size(A);
stepSize = 15;
gridSize = 15;
pixelRatio = 0.3;
fftBar = pixelRatio*gridSize;

k = zeros(ceil(N(1)/stepSize),ceil(N(2)/stepSize));
ff = zeros(ceil(N(1)/stepSize),ceil(N(2)/stepSize));

for i = 2:stepSize:N(1)-(gridSize+1)
    for j = 2:stepSize:N(2)-(gridSize+1)
        C = A(i:i+gridSize,j:j+gridSize);
        k(ceil(i/stepSize),ceil(j/stepSize)) = corr2(C,Z);
        
        fftX = abs(fft(C));
        fftX = mean(fftX(1:fftBar,:),2);
        fftY = abs(fft(C'));
        fftY = mean(fftY(1:fftBar,:),2);
        ff(ceil(i/stepSize),ceil(j/stepSize)) = mean(temp(:));
    end %j
end %i

figure; surf(k);
figure; surf(ff);


%%
i=2000; j=2000;
C=A(i:i+15,j:j+15);
temp = abs(fft(C));
%temp = temp(1:3,:);
tempT = abs(fft(C'));
%tempT = tempT(1:3,:);
temp2 = abs(fft2(C));
figure; subplot(121); surf(temp); subplot(122); surf(tempT);
figure; surf(temp2);

%%
i=2000; j=2000;
C1=A(i:i+3*15,j:j+4*15);
figure; imshow(C1, [0 255]);

i=3000; j=1000;
C2=A(i:i+3*15,j:j+4*15);
figure; imshow(C2, [0 255]);

i=800; j=4000;
C3=A(i:i+3*15,j:j+4*15);
figure; imshow(C3, [0 255]);