fft_size = 2048;
fs = 2e6;
frame_rate = 1000;

window_size = 20;       % Moving window size (in seconds)
window_k = 100;         % Stride 
movmean_k = 20;         % Number of samples used in moving average

% How many vectors do you want to use for the running average
num_avg_window = 25;

% How many samples to average for the baseline 
avg_n = 20;

numFiles = 275;
signal = [];
time = 0; timef = []; time_l=0;

path='/Volumes/USRP/2019-10-07/';
Files=dir('*.bin')
Files

for j=1:length(Files)
    
    %%% Read File %%%
    
    %file = strcat(strcat();
    fileName = Files(j).name;   
    %fileName = 'ac_1.bin';
    
    fileID = fopen(fileName, 'r');
    x = fread(fileID, 'float');

    total_time = length(x)*(1/fs);
    bin_duration = fft_size*(1/fs);
    time_0 = 0:bin_duration:total_time-(1/fs);

    T = length(x)/fft_size;
    spectra = reshape(x,[fft_size,T]);


    % Compute Avreaged frames, every NUM_AVG_WINDOW samples of FFT vectors
    spectra_avg = zeros(fft_size, floor(size(spectra,2)/num_avg_window));
    count = 1;
    for i = 1:num_avg_window:size(spectra,2) - num_avg_window
        spectra_avg(:,count) = mean(spectra(:, i:i + num_avg_window -1), 2);
        count = count + 1;
    end
    if length(timef) ~= 0
        time_l = max(timef);
    end
    time = time_0(1:num_avg_window:length(time_0)-25);
    timef = [timef, time+time_l];
    % Generate Baseline
    %baseline = sum(spectra_avg(:,(1:avg_n)),2)/avg_n;
    % Subtract baseline
    %sig = (spectra_avg-baseline);
    sig_vert = sum(abs(spectra_avg(:,:)));
    
    signal = [signal,sig_vert];
    
    if mod(j, 5) == 0
        plot(signal)
        pause(0.01)
    end
    
    
%     f_title = erase(file, '.mat');
%     plot(Data.time, Data.signal)
%     title(f_title);
%     xlabel('Time (s)')
%     ylabel('Signal')
%     savefig(f_title)
    
end
%sig_norm = normalize(sig_vert, 'center', 'mean');
%sig_avg = movmean(sig_vert, movmean_k);

%figure; plot(sig_avg);