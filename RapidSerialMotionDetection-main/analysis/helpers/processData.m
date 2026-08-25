function [PERFORMANCE, SEQUENCE] = processData(data)
% -------------------------------------------------------------------------
% PROCESS DATA
% -------------------------------------------------------------------------
% This function generates tables for performance measures and for impulse 
% sequence for each trial based on the data structure of the converted mwk2
% file, which contains event, time, and value information.
%
%
% INPUT
%       data        : structure
%           Loaded .mat file with the fields:
%             - time    : vector of timestamps (in µs)
%             - event   : cell array of event labels (char/string)
%             - value   : cell array of event values
%
% OUTPUT
%       PERFORMANCE : table
%           Performance meassures for each trial :
%             - Motion          : label of the current target motion 
%             - Session         : label of the current session
%             - Trial           : number of the current trial
%             - MOT_TARGETS     : number of shown target motions
%             - MOT_RESPONSE    : number of motion responses
%             - MOT_HIT         : number of motion hit responses
%             - MOT_FA          : number of motion false alarm responses
%             - MOT_RT          : reaction time for each motion hit 
%                                 response
%             - LUM_TARGETS     : number of shown luminance changes
%             - LUM_RESPONSE    : number of luminance responses
%             - LUM_HIT         : number of luminance hit responses
%             - LUM_FA          : number of luminance false alarm responses
%             - LUM_RT          : reaction time for each luminance hit 
%                                 response
%
%       SEQUENCE    : table
%           Impulse paramters within the sequence of each trial
%             - Motion          : label of the current target motion 
%             - Session         : label of the current session
%             - Trial           : number of the current trial
%             - Onset           : time stamp of each impulse onset
%             - Direction       : motion direction of each impulse
%             - Validity        : logical index if impulses were valid
%             - Response_Onset  : time stamp of each response onset
% -------------------------------------------------------------------------



% ----- SETTINGS ----------------------------------------------------------

LUM_RESPONSE_WINDOW = [200 800];   % in ms
MOT_RESPONSE_WINDOW = [200 800];   % in ms


% ----- EXTRACT TRIAL NUMBERS ---------------------------------------------

trial_num   = cell2mat(data.value(data.event == 'TRIAL_number'));

trial_start = data.time(data.event == 'TRIAL_start');

trial_end   = data.time(data.event == 'TRIAL_end');


% get valid trials only
is_trial_reset = find(trial_num == 1, 1, 'last') - 1;

trial_num(1:is_trial_reset)     = [];
trial_start(1:is_trial_reset)   = [];
trial_end(1:is_trial_reset)     = [];

is_trial_copy = find(trial_num == trial_num(end), 1, 'first') + 1;

trial_num(is_trial_copy:end)    = [];
trial_start(is_trial_copy:end)  = [];
trial_end(is_trial_copy:end)    = [];


nTrials = numel(trial_num);

fprintf('\t(%.f trials)\n', nTrials)



% ----- EXTRACT SESSION PARAMETERS ----------------------------------------

% trial number
TRIAL = (1:nTrials).';

% attention condition
idx = find(data.event == 'EXP_attention_condition', 1, 'last');
SESSION = repmat(string(data.value{idx}), nTrials, 1);

% motion condition
idx = find(data.event == 'EXP_motion_condition', 1, 'last');
MOTION = repmat(string(data.value{idx}), nTrials, 1);

idx = find(data.event == 'MOT_target_dir', 1, 'last');
target_dir = double(data.value{idx});

% luminance response button
idx = find(data.event == 'LUM_button', 1, 'last');
LUM_BUTTON = data.value{idx};

% motion response button
idx = find(data.event == 'MOT_button', 1, 'last');
MOT_BUTTON = data.value{idx};



% ----- INITIALIZE VARIABLES ----------------------------------------------

% performance variables
MOT_TARGETS     = cell(nTrials,1);
MOT_RESPONSE    = cell(nTrials,1);
MOT_HIT         = cell(nTrials,1);
MOT_FA          = cell(nTrials,1);
MOT_RT          = cell(nTrials,1);

LUM_TARGETS     = cell(nTrials,1);
LUM_RESPONSE    = cell(nTrials,1);
LUM_HIT         = cell(nTrials,1);
LUM_FA          = cell(nTrials,1);
LUM_RT          = cell(nTrials,1);


% impulse variables
IMP_ONSET       = cell(nTrials,1);
IMP_DIR         = cell(nTrials,1);
IMP_VALID       = cell(nTrials,1);
RESPONSE_ONSET  = cell(nTrials,1);



% ----- PERFORMANCE OF EACH TRIAL -----------------------------------------

for tr = 1:nTrials
        
    % index for event within trial borders
    idx = data.time >= trial_start(tr) & ...
          data.time <  trial_end(tr);

    tr_time     = data.time(idx);
    tr_event    = data.event(idx);
    tr_value    = data.value(idx);


    % remove entries that are encoded as cell
    idx = tr_event == "LUM_button" | tr_event == "MOT_button";

    tr_time(idx)    = [];
    tr_event(idx)   = [];
    tr_value(idx)   = [];


    % conver values to double
    tr_value    = cell2mat(cellfun(@double, tr_value, ...
                                   'UniformOutput', false));



    % ----- IMPULSE PARAMETERS --------------------------------------------

    tImp_all    = tr_time(tr_event == 'IMP_counter_all' & ...
                          tr_value > 0);
    nImp_all    = numel(tImp_all);

    tImp_valid  = tr_time(tr_event == 'IMP_counter_valid' & ...
                          tr_value > 0);


    % preallocate index for valid impulses
    idx_valid_imp = false(1, nImp_all);  
    
    % filter out invalid impulses
    for i = 1:nImp_all
        
        % last impulse has to be valid
        if i == nImp_all
            idx_valid_imp(i) = true;
        else

            % check if any valid event falls inside interval
            t_start = tImp_all(i);
            t_end   = tImp_all(i+1);
        
            idx_valid_imp(i) = any(tImp_valid > t_start & ...
                               tImp_valid < t_end);
        end
    end

    IMP_VALID{tr} = idx_valid_imp;
    

    % CHECK:
    % number of valid impulses should match valid impuls counter
    % sum(idx_valid_imp) == numel(tImp_valid);
    

    % get RDP onset time
    RDP_time        = tr_time(tr_event == 'IMP_onset' & ...
                              tr_value > 0);
    IMP_ONSET{tr}   = RDP_time;


    % get RDP direction
    RDP_dir     = tr_value(tr_event == 'RDP_dir');
    RDP_dir     = RDP_dir  - target_dir;           % relative to target
    IMP_DIR{tr} = mod(RDP_dir + 90, 360) - 90;     % scale to -90 to 255



    % ----- TARGET ONSET TIMES --------------------------------------------

    mot_onsets = tr_value(tr_event == 'MOT_target_onset');
    lum_onsets = tr_value(tr_event == 'LUM_target_onset');

    % get time stamp of impulses containing targets
    mot_target_time = RDP_time(logical(mot_onsets));
    lum_target_time = RDP_time(logical(lum_onsets));



    % ----- DEFINE TIME WINDOW OF INVALID RESPONSES -----------------------

    % last valid impulse preceding invalid impusles
    last_valid_before_invalid = find(idx_valid_imp(1:end-1) & ...
                                     ~idx_valid_imp(2:end));

    % preallocate
    exclude_window = nan(numel(last_valid_before_invalid) + 2, 2);


    % get time stamps
    for i = 1:size(exclude_window,1)

        % anytime before the 200 ms after first shown impulse
        if i == 1
            % get first valid impulse
            idx_first_valid = find(idx_valid_imp, 1, 'first');

            t_window_start  = -Inf;
            t_window_end    = RDP_time(idx_first_valid) + 200e3;


        % 1000 ms after last shown impulse
        elseif i == size(exclude_window,1)
            % get last valid impulse
            idx_last_valid  = find(idx_valid_imp, 1, 'last');

            t_window_start  = RDP_time(idx_last_valid) + 1000e3;
            t_window_end    = Inf;

        % during invalid impulses
        else
            % get last valid impulse before invalid impulses
            idx_before_break = last_valid_before_invalid(i-1);

            % get next valid impulse after invalid impulses
            idx_after_break = idx_before_break + ...
                              find(idx_valid_imp(...
                                   idx_before_break+1:end), 1, 'first');

            t_window_start  = RDP_time(idx_before_break);
            t_window_end    = RDP_time(idx_after_break);
        end

        % add to array
        exclude_window(i,:) = [t_window_start t_window_end];
    end


    % adjust window for luminance responses
    idx = diff(exclude_window, 1, 2) > LUM_RESPONSE_WINDOW(end) * 1e3;
    lum_exclude_window = exclude_window(idx,:);

    % adjust window for motion responses
    idx = diff(exclude_window, 1, 2) > MOT_RESPONSE_WINDOW(end) * 1e3;
    mot_exclude_window = exclude_window(idx,:);



    % ----- MOTION RESPONSE ONSET TIMES -----------------------------------

    mot_resp_time = tr_time(tr_event == MOT_BUTTON & ...
                            tr_value > 0);
    

    % exclude responses within exclusion window
    keep_response = true(size(mot_resp_time));
    
    for i = 1:size(mot_exclude_window,1)
        in_window = mot_resp_time >= mot_exclude_window(i,1) & ...
                    mot_resp_time <  mot_exclude_window(i,2);

        keep_response = keep_response & ~in_window;            
    end

    fprintf('\t\t\t\t\t(%d not kept MOT responses)\n', sum(keep_response == 0))
    mot_resp_time = mot_resp_time(keep_response);

    RESPONSE_ONSET{tr} = mot_resp_time;



    % ----- LUMINANCE RESPONSE ONSET TIMES --------------------------------
    
    lum_resp_time = tr_time(tr_event == LUM_BUTTON & ...
                            tr_value > 0);

    
    % exclude responses before and after last impulse
    keep_response = true(size(lum_resp_time));
    
    for i = 1:size(lum_exclude_window,1)
        
        % responses within exclusion window
        in_window = lum_resp_time >= lum_exclude_window(i,1) & ...
                    lum_resp_time <  lum_exclude_window(i,2);
    
        keep_response = keep_response & ~in_window;            
    end
    
    fprintf('\t\t\t\t\t(%d not kept LUM responses)\n', sum(keep_response == 0))
    lum_resp_time = lum_resp_time(keep_response);



    % ----- PERFORMANCE FOR LUMINANCE DETECTION ---------------------------

    [nHits, nFA, RT] = getPerformance(lum_target_time, ...
                                      lum_resp_time, ...
                                      LUM_RESPONSE_WINDOW);

    LUM_TARGETS{tr}     = numel(lum_target_time);
    LUM_RESPONSE{tr}    = numel(lum_resp_time);
    LUM_HIT{tr}         = nHits;
    LUM_FA{tr}          = nFA;
    LUM_RT{tr}          = RT;



    % ----- PERFORMANCE FOR MOTION DETECTION ------------------------------

    [nHits, nFA, RT] = getPerformance(mot_target_time, ...
                                      mot_resp_time, ...
                                      MOT_RESPONSE_WINDOW);

    MOT_TARGETS{tr}     = numel(mot_target_time);
    MOT_RESPONSE{tr}    = numel(mot_resp_time);
    MOT_HIT{tr}         = nHits;
    MOT_FA{tr}          = nFA;
    MOT_RT{tr}          = RT;
end



% ----- AGGREGATE TRIAL DATA ----------------------------------------------

vars_name   = ["Motion",        "Session",      "Trial",  ...
               "MOT_TARGETS",   "MOT_RESPONSE", "MOT_HIT", ...
               "MOT_FA",       "MOT_RT" ...
               "LUM_TARGETS",   "LUM_RESPONSE", "LUM_HIT", ...
               "LUM_FA",       "LUM_RT"];

PERFORMANCE = table(MOTION,         SESSION,        TRIAL , ...
                    MOT_TARGETS,    MOT_RESPONSE,   MOT_HIT, ...
                    MOT_FA,         MOT_RT, ...
                    LUM_TARGETS,    LUM_RESPONSE,   LUM_HIT, ...
                    LUM_FA,         LUM_RT, ...
                    'VariableNames', vars_name);



% ----- AGGREGATE IMPULSE PARAMETER ---------------------------------------

vars_name   = ["Motion",        "Session",      "Trial",  ...
               "Onset",         "Direction", ...
               "Validity",      "Response_Onset"];

SEQUENCE    = table(MOTION,         SESSION,        TRIAL , ...
                    IMP_ONSET,      IMP_DIR,        IMP_VALID, ...
                    RESPONSE_ONSET, ...
                    'VariableNames', vars_name);
end

