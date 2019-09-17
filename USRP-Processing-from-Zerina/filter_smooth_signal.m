%% Get rid outliers
for i=1:length(signal)
    if signal(i) == 0
        signal(i) = signal(i+1);
    end
end

%% Get Time
time = 0:0.0256:0.0256*length(signal);
time = time(1:length(time)-1);
time = time/3600;

%% Normalize and filter
filt_order = 3.5e3;
signal_norm = normalize(signal, 'range');
signal_smooth = medfilt1(signal_norm, filt_order);
signal_smooth(1) = signal_smooth(2);
 
subplot(3,1,1); plot(time, signal);
subplot(3,1,2); plot(time, signal_norm);
subplot(3,1,3); plot(time, signal_smooth);
% %% Find local min and max
% min_prominence = 0.01;
% [lmin, minp] = islocalmin(signal_smooth, 'MinProminence',min_prominence);
% [lmax, maxp] = islocalmax(signal_smooth, 'MinProminence',min_prominence);
% 
% %% Plot signal
% figure;
% clf; hold on;
% plot(time, signal_smooth);
% plot(time(lmin), signal_smooth(lmin), 'r*')
% plot(time(lmax), signal_smooth(lmax), 'b*')
