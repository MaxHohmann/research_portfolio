function [RMC_1_mat] = getMRC_1(SEQUENCE)
% -------------------------------------------------------------------------
% MOTION REVERSE CORRELATION (FIRST ORDER)
% -------------------------------------------------------------------------
% This function performs the first order Motion Reverse Correlation (MRC). 
% It computes the (normalized) propabilities for each impuses with certain
% motion direction at a certain time latency to precede a response onset.
% Probabilities time courses (across all latencies) for each directions of 
% the impulses are low-passed at 4 Hz to reduce noise. Probabilities are 
% returned as table for further analysis.
%
%
% INPUT
%       SEQUENCE    : table
%           Impulse paramters within the sequence of each trial
%             - Motion          : label of the current target motion 
%             - Session         : label of the current session
%             - Trial           : number of the current trial
%             - Onset           : time stamp of each impulse onset
%             - Direction       : motion direction of each impulse
%             - Validity        : logical index if impulses were valid
%             - Response_Onset  : time stamp of each response onset
%
% OUTPUT
%       RMC_1_mat   : table
%           Correlation values for each impulse across motion direction and
%           at latency bin to precede a response onset
%             - Latency     : bin of each time lag (in ms) between impulse 
%                             onset and response onset
%             - Direction   : bin of each motion direction (-90 to 255 deg)
% -------------------------------------------------------------------------



% ----- SETTINGS ----------------------------------------------------------

latency_min = -1000;
latency_max = 300;

lag_bins    = (latency_min:50:latency_max);     % latency bin
dir_bins    = (-90 : 22.5 : 255);      	        % directions bin

nLag = numel(lag_bins); % substract one lag bin (325)???
nDir = numel(dir_bins);



% ----- COUNT IMPULSES ACROSS TRIALS --------------------------------------

% preallocate
COUNT_MAT = zeros(nLag, nDir);


% iteration over trials
for tr = 1:size(SEQUENCE, 1)

    % get paramters of corresponding trial
    IMP_ONSET       = SEQUENCE.Onset{tr};
    IMP_DIR         = SEQUENCE.Direction{tr};
    IMP_VALID       = SEQUENCE.Validity{tr};
    RESPONSE_ONSET  = SEQUENCE.Response_Onset{tr};


    % filter out any invalid impulses
    IMP_ONSET(~IMP_VALID)   = [];
    IMP_DIR(~IMP_VALID)     = [];


    
    % ----- GET DIRECTION AND LATENCY -------------------------------------

    % iteration over responses
    for resp = 1:numel(RESPONSE_ONSET)

        % latencies between impulse and response onsey
        latencies = IMP_ONSET - RESPONSE_ONSET(resp);    

        % extract impulses at latencies within analysis window
        imp_in_win = find(latencies >= latency_min * 1e3 & ...
                          latencies <= latency_max * 1e3);

        
        % count impulses according to latency and motion direction
        if ~isempty(imp_in_win)
            
            % iterate over impulses of interest
            for i = 1:numel(imp_in_win)

                idx     = imp_in_win(i);                    % impulse index
                dir_idx = find(dir_bins == IMP_DIR(idx),1); % direction bin
                lag_idx = discretize(latencies(idx), ...    % latency bin
                                     lag_bins * 1e3);   

                % increase counter
                COUNT_MAT(lag_idx, dir_idx) = ...
                    COUNT_MAT(lag_idx, dir_idx) + 1;
            end
        end
    end
end



% ----- NORMALIZATION -----------------------------------------------------

% normalize by total number of impulses at the same time lag
rowSum = sum(COUNT_MAT, 2, 'omitnan');
rowSum(rowSum == 0) = 1;            % prevent division by zero

COUNT_MAT = COUNT_MAT ./ rowSum;    % probability for each impulse



% ----- SMOOTHING ---------------------------------------------------------

% low-pass Butterworth filter
bin_width   = diff(lag_bins) ./ 1e3;    % bin witdth in s
F.s         = 1 / bin_width(1);	        % sampling rate (Hz)
F.cut       = 4;           	            % cutoff frequency (Hz)
F.n         = 2;               	        % filter order
[b, a]      = butter(F.n, F.cut / (F.s / 2), 'low');

% zero-phase filtering
COUNT_MAT   = filtfilt(b, a, COUNT_MAT);



% ----- CREATE CORRELATION TABLE ------------------------------------------

dir_labels  = "Direction_" + string(dir_bins);  % label for directions

% create correlation table
RMC_1_mat  = array2table(COUNT_MAT, ...
                         'VariableNames', dir_labels);

% add latency as first column
RMC_1_mat  = addvars(RMC_1_mat, (lag_bins + 25)', ...
                     'Before', 1, ...
                     'NewVariableNames', 'Latency');
end

