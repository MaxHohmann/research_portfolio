function [retval] = RSMD_onlineAnalysis(data, valuesMW)
% -------------------------------------------------------------------------
% RAPID SERIAL MOTION DETECTION - ONLINE ANALYSIS
% -------------------------------------------------------------------------
% Analyses stimulus timing and subject performance during Dual-RSVP Task of
% the Rapid Serial Motion detection experiment. Performance for luminance 
% change detection task and motion detection task is computed. Additional
% impulse on-/offset timing calculated. Figures are created displaying the
% current and behavioral performance and impulse timing. The average of 
% performance and impulses timing is also printed in the console.
% 
% This script is called on each chnage of the 'ML_sync' variable in MWorks 
% from 1 (trial start) to 0 (trial end).
%
% Version:  1.5.0
% Date:     21/08/2026  
% Author:  	Maximilian Hohmann
%         	mhohmann@dpz.eu
%          	maximilian.hohmann@stud.uni-goettingen.de
% -------------------------------------------------------------------------



global values;



% ----- HELPER FUNCTION ---------------------------------------------------

function d = compute_dprime(hit_rate, fa_rate)
    
% calculate d-prime
eps = 1e-5;
hit_rate = min(max(hit_rate, eps), 1-eps);
fa_rate  = min(max(fa_rate, eps), 1-eps);

d = norminv(hit_rate) - norminv(fa_rate);
end



% ----- INITIALIZE --------------------------------------------------------

if nargin == 1
    nMax = 40;

    % assigned buttons
    values.lum_button       = [];
    values.mot_button       = [];

    % target and response counts
    values.lum_press_count  = nan(1,nMax);  % responses
    values.lum_target_count = nan(1,nMax);  % targets
    
    values.mot_press_count  = nan(1,nMax);  % responses
    values.mot_target_count = nan(1,nMax);  % targets

    % performance for luminance change detection
    values.lum_hit_rate     = nan(1,nMax);
    values.lum_FA_rate      = nan(1,nMax);
    values.lum_dprime       = nan(1,nMax);
    
    values.lum_RT_median    = nan(1,nMax);
    values.lum_RT_max       = nan(1,nMax);
    values.lum_RT_min       = nan(1,nMax);
    values.lum_RT_std       = nan(1,nMax);

    % performance for target motion detection
    values.mot_hit_rate     = nan(1,nMax);
    values.mot_FA_rate      = nan(1,nMax);
    values.mot_dprime       = nan(1,nMax);

    values.mot_RT_median    = nan(1,nMax);
    values.mot_RT_max       = nan(1,nMax);
    values.mot_RT_min       = nan(1,nMax);
    values.mot_RT_std       = nan(1,nMax);

    close all;
    figure(1);
    
    valuesMW = 0;

    addpath('/Users/cnl/Documents/MWorks/MatLab/readData');
end


% read trial data
trial = MW_readTrial(data);

% current trial number
idx = double(trial.TRIAL_number.data);

% reset values 
if idx == 1
    f = fieldnames(values);
    for i = 1:length(f)
        values.(f{i})(:) = nan;
    end
end



% ----- ASSIGN RESPONSES BUTTONS ------------------------------------------

values.lum_button = trial.LUM_button(end).data;
values.mot_button = trial.MOT_button(end).data;



% ----- LUMINANCE RESPONSES -----------------------------------------------

% response onset
if isfield(trial, values.lum_button) && ~isempty(trial.(values.lum_button))
    
    lum_button_times    = double(trial.(values.lum_button).time);
    lum_button_idx      = logical(trial.(values.lum_button).data);

    % filter entries for presses
    lum_button_times(~lum_button_idx) = [];
else
    lum_button_times = [];
end

values.lum_press_count(idx) = numel(lum_button_times);


% target onset
if isfield(trial,'LUM_target_onset')
    
    lum_onsets = double(trial.LUM_target_onset.time(trial.LUM_target_onset.data == 1));
    
    if ~isempty(lum_onsets) && ...
            numel(lum_onsets) == trial.LUM_target_counter.data(end)
        
        valid_lum_times = lum_onsets;

    else
        valid_lum_times = [];       % initialize
        
        for i = 1:numel(lum_onsets) % check for coresponding valid count
            
            rel_Delay = trial.IMP_counter_valid.time - lum_onsets(i);
            
            if any(rel_Delay > 0 & rel_Delay < 180e3)
                valid_lum_times(end+1) = lum_onsets(i);     %#ok<AGROW>
            end
        end
    end
else
    valid_lum_times = [];
end

values.lum_target_count(idx) = trial.LUM_target_counter.data(end);


% compute performance
nTargets    = length(valid_lum_times);
hits        = false(1,nTargets);
rt          = nan(1,nTargets);
nFA         = 0;


for r = 1:length(lum_button_times)

    dt = lum_button_times(r) - valid_lum_times;
    dt(dt < 0) = inf;
    

    if isempty(dt)
        continue;
    end

    [min_dt, idx_min] = min(dt);

    if isinf(min_dt)
        continue;
    end

    % hit (200 ms to 1000 ms)
    if min_dt >= 200e3 && min_dt <= 1000e3
        if ~hits(idx_min)
            hits(idx_min) = true;
            rt(idx_min) = min_dt / 1e3;
        end

    % false alarm
    else
        nFA = nFA + 1;
    end
end

nHits   = sum(hits);


values.lum_hit_rate(idx)    = nHits / nTargets;
values.lum_FA_rate(idx)     = nFA / (80 - nTargets);

values.lum_dprime(idx)      = compute_dprime(values.lum_hit_rate(idx), values.lum_FA_rate(idx));

values.lum_RT_median(idx)   = median(rt,'omitnan');
values.lum_RT_max(idx)      = max(rt,[],'omitnan');
values.lum_RT_min(idx)      = min(rt,[],'omitnan');
values.lum_RT_std(idx)      = std(rt,'omitnan');



% ----- MOTION RESPONSES --------------------------------------------------

% response onset
if isfield(trial, values.mot_button) && ~isempty(trial.(values.mot_button))  

    mot_button_times    = double(trial.(values.mot_button).time);
    mot_button_idx      = logical(trial.(values.mot_button).data);
    
    % filter entries for presses
    mot_button_times(~mot_button_idx) = [];  
else
    mot_button_times = [];
end

values.mot_press_count(idx) = numel(mot_button_times);


% target onset
if isfield(trial,'MOT_target_onset')

    mot_onsets = double(trial.MOT_target_onset.time(trial.MOT_target_onset.data == 1));
    
    if  ~isempty(mot_onsets) && ...
            numel(mot_onsets) == trial.MOT_target_counter.data(end)
        
        valid_mot_times = mot_onsets;
        
    else
        valid_mot_times = [];       % initialize
        
        for i = 1:numel(mot_onsets)	% check for coresponding valid count
            
            rel_Delay = trial.IMP_counter_valid.time - mot_onsets(i);
            
            if any(rel_Delay > 0 & rel_Delay < 180e3)
                valid_mot_times(end+1) = mot_onsets(i);     %#ok<AGROW>
            end
        end
    end
else
    valid_mot_times = [];
end

values.mot_target_count(idx) = trial.MOT_target_counter.data(end);


% compute performance
nTargets    = length(valid_mot_times);
hits        = false(1,nTargets);
rt          = nan(1,nTargets);
nFA         = 0;

for r = 1:length(mot_button_times)
    resp_time = mot_button_times(r);

    dt = resp_time - valid_mot_times;
    dt(dt < 0) = inf;

    if isempty(dt)
        continue;
    end

    [min_dt, idx_min] = min(dt);

    if isinf(min_dt)
        continue;
    end

    % hit (200 ms to 800 ms)
    if min_dt >= 200e3 && min_dt <= 800e3
        if ~hits(idx_min)
            hits(idx_min) = true;
            rt(idx_min) = min_dt / 1e3;
        end

    % false alarm
    else
        nFA = nFA + 1;
    end
end

nHits   = sum(hits);


values.mot_hit_rate(idx)    = nHits / nTargets;
values.mot_FA_rate(idx)     = nFA / (80 - nTargets);

values.mot_dprime(idx)      = compute_dprime(values.mot_hit_rate(idx), values.mot_FA_rate(idx));

values.mot_RT_median(idx)   = median(rt,'omitnan');
values.mot_RT_max(idx)      = max(rt,[],'omitnan');
values.mot_RT_min(idx)      = min(rt,[],'omitnan');
values.mot_RT_std(idx)      = std(rt,'omitnan');



% ----- AGGREGATE PERFORMANCE ---------------------------------------------

lum_hit_mean    = mean(values.lum_hit_rate,'omitnan');
lum_FA_mean     = mean(values.lum_FA_rate,'omitnan');
lum_d_mean      = mean(values.lum_dprime,'omitnan');

mot_hit_mean    = mean(values.mot_hit_rate,'omitnan');
mot_FA_mean     = mean(values.mot_FA_rate,'omitnan');
mot_d_mean      = mean(values.mot_dprime,'omitnan');

lum_RT_med_all  = median(values.lum_RT_median,'omitnan');
lum_RT_std_all  = std(values.lum_RT_median,'omitnan');

mot_RT_med_all  = median(values.mot_RT_median,'omitnan');
mot_RT_std_all  = std(values.mot_RT_median,'omitnan');



% ----- IMPULSE TIMING (on-/offsets) --------------------------------------

expected_shown  = 150;  % expected onset duration (ms)
expected_blank  = 75;   % expected offset duration (ms)

t_imp = double(trial.IMP_onset.time);
v_imp = double(trial.IMP_onset.data);

wait_onset = t_imp(end);   % entry after last imp offset
t_imp(end) = [];
v_imp(end) = [];

shown_onsets    = t_imp(v_imp == 1); 	% 1 = impulse displayed
blank_onsets    = t_imp(v_imp == 0); 	% 0 = impusle withdrawn

nPairs = numel(shown_onsets);


% initialize duration arrays
shown_durations = nan(1,nPairs);
blank_durations = nan(1,nPairs);

% shown duration (shown to blank onset)
for i = 1:nPairs
    shown_durations(i) = (blank_onsets(i) - shown_onsets(i)) / 1e3;
end

% blank duration (blank to next shown onset)
for i = 1:nPairs
    if i < nPairs
        blank_durations(i) = (shown_onsets(i+1) - blank_onsets(i)) / 1e3;
    else
        blank_durations(i) = (wait_onset - blank_onsets(i)) / 1e3;
    end
end


% indicate if impulse contains target onsets
lum_imp_idx = false(size(shown_onsets));
mot_imp_idx = false(size(shown_onsets));

% onset of luminance change
for i = 1:length(lum_onsets)
    for k = 1:numel(shown_onsets)
        
        % check for target within impulse interval
        if lum_onsets(i) < shown_onsets(k) && k == 1
            lum_imp_idx(k) = true;
            
        elseif lum_onsets(i) < shown_onsets(k) && lum_onsets(i) > shown_onsets(k-1) && k > 1
            lum_imp_idx(k) = true;
        end
    end
end

% onset of target motion
for i = 1:length(mot_onsets)
    for k = 1:numel(shown_onsets)

        % check for target within impulse interval
        if mot_onsets(i) < shown_onsets(k) && k == 1
            mot_imp_idx(k) = true;
            
        elseif mot_onsets(i) < shown_onsets(k) && mot_onsets(i) > shown_onsets(k-1) && k > 1
            mot_imp_idx(k) = true;
        end
    end
end



% ----- PLOTTING ----------------------------------------------------------

figure(1); clf;

x_max = ceil(idx/4)*4 + 2;
x_limits = [.5 x_max];



% --- target and response counts ---
subplot(3,3,[2 3]); cla; hold on;

plot(values.lum_press_count, '-', 'Color', [0 0 0.8], 'LineWidth', 2.5); 
plot(values.lum_target_count, ':', 'Color', [0.2 0.2 0.8], 'LineWidth', 2.5);

plot(values.mot_press_count, '-', 'Color', [0.8 0 0], 'LineWidth', 2.5);
plot(values.mot_target_count, ':', 'Color', [0.8 0.2 0.2], 'LineWidth', 2.5);

max_count = max([values.lum_press_count values.mot_press_count ...
                 values.lum_target_count values.mot_target_count], [], 'omitnan');

if isempty(max_count) || isnan(max_count)
    max_count = 1;
end

xlim(x_limits);
ylim([0 max_count+1]);
grid on;

xlabel('Trial');
ylabel('Count');
title('Responses vs Targets');

legend({'LUM Resp.','LUM Targets','MOT Resp.','MOT Targets'}, ...
       'Location','northeast');


   
% --- Reaction Time ---
subplot(3,3,[5 6]); cla; hold on;
 
plot(values.lum_RT_median, '-', 'Color', [0 0 0.8], 'LineWidth', 2.5);
plot(values.mot_RT_median, '-', 'Color', [0.8 0 0], 'LineWidth', 2.5);

ylim([200 1000]);
xlim(x_limits);
grid on;

xlabel('Trial');
ylabel('RT [ms]');
title('Reaction Time');

legend({'Luminance', 'Motion'}, ...
    'Location','northeast');



% --- Hit Rate ---
subplot(3,3,7); cla; hold on;

plot(values.lum_hit_rate,'-', 'Color', [0 0 0.8], 'LineWidth', 1.5); 
plot(values.mot_hit_rate,'-', 'Color', [0.8 0 0], 'LineWidth', 1.5); 

xlim(x_limits);
ylim([0 1]);
grid on;

xlabel('Trial');
ylabel('Rate');
title('Hit Rate');



% --- False Alarm Rate ---
subplot(3,3,8); cla; hold on;
 
plot(values.lum_FA_rate,'-', 'Color', [0 0 0.8], 'LineWidth', 1.5); 
plot(values.mot_FA_rate,'-', 'Color', [0.8 0 0], 'LineWidth', 1.5); 

xlim(x_limits);
ylim([0 0.06]);
grid on;

xlabel('Trial');
ylabel('Rate');
title('False Alarm Rate');



% --- sensitivity ---
subplot(3,3,9); cla; hold on;
 
plot(values.lum_dprime,'-', 'Color', [0 0 0.8], 'LineWidth', 1.5); 
plot(values.mot_dprime,'-', 'Color', [0.8 0 0], 'LineWidth', 1.5); 

xlim(x_limits);
ylim([-5 10]);
grid on;

xlabel('Trial');
ylabel('Rate');
title('d'' Rate (Sensitivity)');



% --- stimulus onset timing ---
subplot(3,3,1); cla; hold on;

shown_time_max  = expected_shown + 1.5;
shown_time_min  = expected_shown - 1.5;

% actual duration
plot(shown_durations, '-', 'Color', [0 0 0], 'LineWidth', 1);

% expected duration
line([0 numel(shown_durations)], [expected_shown; expected_shown], ...
 'Color', [0 0 0], 'LineStyle', '-', 'LineWidth', 1);

xlabel('impulse index');
ylabel('duration [ms]');
title(sprintf('Onset Timing (Trial %d, N=%d)', idx, numel(shown_durations)));
xlim([0 max(1,numel(shown_durations)+1)]);
ylim([shown_time_min, shown_time_max]);



% draw line for impulses containing luminance change
lum_imp = find(lum_imp_idx);
for i=1:numel(lum_imp)

    line([lum_imp(i), lum_imp(i)], [shown_time_min, shown_time_max], ...
    'Color', [0 0 0.8], 'LineStyle', '--', 'LineWidth', 1);
end

% draw line for impusles containing target motion
mot_imp = find(mot_imp_idx);
for i=1:numel(mot_imp)

    line([mot_imp(i), mot_imp(i)], [shown_time_min, shown_time_max], ...
    'Color', [0.8 0 0], 'LineStyle', '--', 'LineWidth', 1);

end


% --- stimulus offset timing ---
subplot(3,3,4); cla; hold on;

blank_time_max  = expected_blank + 1.5;
blank_time_min  = expected_blank - 1.5;

% actual duration
plot(blank_durations, '-', 'Color', [0 0 0], 'LineWidth', 1);

% expected duration
line([0 numel(blank_durations)], [expected_blank, expected_blank], ...
 'Color', [0 0 0], 'LineStyle', '-', 'LineWidth', 1);

xlabel('impulse index');
ylabel('duration [ms]');
title(sprintf('Offset Timing (Trial %d, N=%d)', idx, numel(blank_durations)));
xlim([0 max(1,numel(blank_durations)+1)]);
ylim([blank_time_min, blank_time_max]);


% draw line for impulses containing luminance change
lum_imp = find(lum_imp_idx);
for i=1:numel(lum_imp)

    line([lum_imp(i), lum_imp(i)], [blank_time_min, blank_time_max], ...
    'Color', [0 0 0.8], 'LineStyle', '--', 'LineWidth', 1);

end

% draw line for impulses containing target motion
mot_imp = find(mot_imp_idx);
for i=1:numel(mot_imp)

    line([mot_imp(i), mot_imp(i)], [blank_time_min, blank_time_max], ...
    'Color', [0.8 0 0], 'LineStyle', '--', 'LineWidth', 1);

end


% ----- OUTPUT ------------------------------------------------------------
fprintf('\n=====> Trial %d <=====\n', idx);

fprintf('--- Luminance ---\n');
fprintf('\tHit Rate    \t: %.3f\n', values.lum_hit_rate(idx));
fprintf('\tFA Rate     \t: %.3f\n', values.lum_FA_rate(idx));
fprintf('\td''       \t\t: %.3f\n', values.lum_dprime(idx));
fprintf('\tRT        \t\t: %.f ± %.f ms\n', values.lum_RT_median(idx), values.lum_RT_std(idx));

fprintf('--- Motion ---\n');
fprintf('\tHit Rate    \t: %.2f\n', values.mot_hit_rate(idx));
fprintf('\tFA Rate     \t: %.2f\n', values.mot_FA_rate(idx));
fprintf('\td''       \t\t: %.2f\n', values.mot_dprime(idx));
fprintf('\tRT        \t\t: %.f ± %.f ms\n', values.mot_RT_median(idx), values.mot_RT_std(idx));

fprintf('\n=====> AGGREGATED <=====\n');

fprintf('--- Luminance ---\n');
fprintf('\tHit Rate    \t: %.3f\n', lum_hit_mean);
fprintf('\tFA Rate     \t: %.3f\n', lum_FA_mean);
fprintf('\td''       \t\t: %.3f\n', lum_d_mean);
fprintf('\tRT        \t\t: %.f ± %.f ms\n', lum_RT_med_all, lum_RT_std_all);

fprintf('--- Motion ---\n');
fprintf('\tHit Rate    \t: %.3f\n', mot_hit_mean);
fprintf('\tFA Rate     \t: %.3f\n', mot_FA_mean);
fprintf('\td''       \t\t: %.3f\n', mot_d_mean);
fprintf('\tRT        \t\t: %.f ± %.f ms\n', mot_RT_med_all, mot_RT_std_all);

    
fprintf('\n=====> TIMING <=====\n'); 
fprintf('\tOnset    \t\t: %.1f ± %.1f ms\n', ...
    median(shown_durations,'omitnan'), std(shown_durations,'omitnan'));
fprintf('\tOffset   \t\t: %.1f ± %.1f ms\n', ...
    median(blank_durations,'omitnan'), std(blank_durations,'omitnan'));


retval = valuesMW;
end

