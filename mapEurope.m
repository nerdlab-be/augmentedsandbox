% Run to obtain the water and mountain estimation of Europe

clear all;
close all;
clc;

%%
[A,cmapA,RA] = geotiffread('elevation1x1_new.tif');
[B,cmapB,RB] = geotiffread('water_out.tif');


N = size(A);
stepSize = 15;
gridSize = 15;
B=double(B)./(100*gridSize^2);

water = zeros(ceil(N(1)/stepSize),ceil(N(2)/stepSize));
mountain = zeros(ceil(N(1)/stepSize),ceil(N(2)/stepSize));
k=1; l=1;
for i = 1:stepSize:N(1)-(gridSize+1)
    for j = 1:stepSize:N(2)-(gridSize+1)
        C = A(i:i+gridSize,j:j+gridSize);
        D = B(i:i+gridSize,j:j+gridSize);
        Cvec=C(:);
        tempMountain = prctile(Cvec, 90)-prctile(Cvec, 10);
        mountain(k,l) = tempMountain;
        water(k,l) = sum(D(:));
        l=l+1;
    end %j
    k=k+1;
    l=1;
end %i
mountain = mountain/max(mountain(:));
water = water/max(water(:));

figure; surf(mountain,'edgecolor', 'none');
figure; surf(water,'edgecolor', 'none');

%% Save to numpy
mat2np(mountain,'mountainEurope15_15.pkl','float64');
mat2np(water, 'waterEurope15_15.pkl', 'float64');